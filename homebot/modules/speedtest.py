from homebot import get_config
from homebot.logging import LOGE, LOGI, LOGD
from homebot.modules_manager import register

# Module-specific imports
from speedtest import Speedtest

@register(commands=['speedtest'])
def speedtest(update, context):
	message_id = update.message.reply_text("Running speedtest...").message_id
	LOGI("Started")
	speedtest = Speedtest()
	speedtest.get_best_server()
	speedtest.download()
	speedtest.upload()
	speedtest.results.share()
	results_dict = speedtest.results.dict()
	download = str(results_dict["download"] // 10 ** 6)
	upload = str(results_dict["upload"] // 10 ** 6)
	context.bot.edit_message_text(chat_id=update.message.chat_id, message_id=message_id,
								  text="Download: " + download + " mbps\nUpload: " + upload + " mbps")
	LOGI("Finished, download: " + download + " mbps, upload: " + upload + " mbps")
