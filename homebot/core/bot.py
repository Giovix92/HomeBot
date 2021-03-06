from homebot import modules
from homebot.core.error_handler import error_handler
from homebot.core.logging import LOGE, LOGI
from telegram import Bot
from telegram.ext import Dispatcher, JobQueue, Updater
from telegram.utils.request import Request
from threading import Event
from queue import Queue

class HomeBotDispatcher(Dispatcher):
	"""
	HomeBot dispatcher.
	"""
	def __init__(self,
				 bot: 'Bot',
				 update_queue: Queue,
				 workers: int = 4,
				 exception_event: Event = None,
				 job_queue: 'JobQueue' = None):
		"""
		Initialize the dispatcher and its modules.
		"""
		super().__init__(bot, update_queue, workers=workers,
						 exception_event=exception_event, job_queue=job_queue)

		self.add_error_handler(error_handler, True)

		self.modules = []

		LOGI("Parsing modules")
		for module in modules:
			try:
				module_instance = module()
			except Exception as e:
				LOGE(f"Error initializing module {module.name}, will be skipped\n"
					 f"Error: {e}")
			else:
				self.modules.append(module_instance)
		LOGI("Modules parsed")

		LOGI("Loading modules")
		for module in self.modules:
			self.load_module(module)
		LOGI("Modules loaded")

	def load_module(self, module):
		"""
		Load a provided module and add its command handler
		to the bot's dispatcher.
		"""
		LOGI(f"Loading module {module.name}")
		module.set_status("Starting up")

		for command in module.commands:
			self.add_handler(command.handler)

		module.set_status("Running")
		LOGI(f"Module {module.name} loaded")

	def unload_module(self, module):
		"""
		Unload a provided module and remove its command handler
		from the bot's dispatcher.
		"""
		LOGI(f"Unloading module {module.name}")
		module.set_status("Stopping")

		for command in module.commands:
			self.remove_handler(command.handler)

		module.set_status("Disabled")
		LOGI(f"Module {module.name} unloaded")

class HomeBotUpdater(Updater):
	"""
	HomeBot updater.
	"""
	def __init__(
		self,
		token: str = None,
		workers: int = 4,
	):
		"""
		Initialize the updater.
		"""
		con_pool_size = workers + 4
		request_kwargs = {'con_pool_size': con_pool_size}
		self._request = Request(**request_kwargs)
		self.bot = Bot(token, request=self._request)

		update_queue: Queue = Queue()
		job_queue = JobQueue()
		exception_event = Event()
		dispatcher = HomeBotDispatcher(
			self.bot,
			update_queue,
			job_queue=job_queue,
			workers=workers,
			exception_event=exception_event
		)
		job_queue.set_dispatcher(dispatcher)

		super().__init__(dispatcher=dispatcher, workers=None)
