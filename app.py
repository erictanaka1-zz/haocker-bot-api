import json, base64
from ibm_watson import AssistantV2, SpeechToTextV1, TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

from flask import Flask, render_template, request, Response, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS

app = Flask(__name__)
socketio = SocketIO(app)
CORS(app)

app.config['JSON_AS_ASCII'] = False

####################################################################################################
@app.route('/', methods=['GET'])
def main():
  return app.send_static_file('index.html')
####################################################################################################
@app.route('/api/conversation', methods=['GET'])
def conversationGet():
	authenticator = IAMAuthenticator('qfOtGUqRjdqld9iT9T8MP54jpCduNAiHxGp8wxBLyEj_')
	assistant = AssistantV2(version='2021-06-14', authenticator=authenticator)
	assistant.set_service_url('https://api.us-east.assistant.watson.cloud.ibm.com/instances/0ab409b1-6d71-4728-937e-a3c554fb561b')

	#####	CREATING SESSION #####
	session = assistant.create_session(
		assistant_id='d51d9cd1-7aae-4b79-a421-a3011081800e'
	).get_result()


	#####	Session ID #####
	sessionId = json.loads(json.dumps(session))
	sessionIdValue = sessionId['session_id']
	#print(sessionId['session_id'])

	#####	SEND MESSAGE AND GET RESPONSE #####
	response = assistant.message(
			assistant_id='d51d9cd1-7aae-4b79-a421-a3011081800e',
			session_id=sessionIdValue,
			input={
					'message_type': 'text',
					'text': ''
			}
	).get_result()	

	# Descomentar essas duas linhas abaixo se quiser gerar um arquivo json com o resultado da chamada de API do Watson
	# with open('./response.json', 'w', encoding='utf-8') as respFile:
	#	json.dump(response, respFile, ensure_ascii=False)

	#####	DELETING SESSION #####
	assistant.delete_session("d51d9cd1-7aae-4b79-a421-a3011081800e", "{}".format(sessionIdValue)).get_result()

	return response
####################################################################################################
@app.route('/api/conversation', methods=['POST'])
def conversation():
	authenticator = IAMAuthenticator('qfOtGUqRjdqld9iT9T8MP54jpCduNAiHxGp8wxBLyEj_')
	assistant = AssistantV2(version='2021-06-14', authenticator=authenticator)
	assistant.set_service_url('https://api.us-east.assistant.watson.cloud.ibm.com/instances/0ab409b1-6d71-4728-937e-a3c554fb561b')

	#####	CREATING SESSION #####
	session = assistant.create_session(
		assistant_id='d51d9cd1-7aae-4b79-a421-a3011081800e'
	).get_result()


	#####	Session ID #####
	sessionId = json.loads(json.dumps(session))
	sessionIdValue = sessionId['session_id']
	#print(sessionId['session_id'])

	inputText = request.form.get("inputTxt")
	print(inputText)

	#####	SEND MESSAGE AND GET RESPONSE #####
	response = assistant.message(
			assistant_id='d51d9cd1-7aae-4b79-a421-a3011081800e',
			session_id=sessionIdValue,
			input={
					'message_type': 'text',
					'text': inputText
			}
	).get_result()	

	# Descomentar essas duas linhas abaixo se quiser gerar um arquivo json com o resultado da chamada de API do Watson
	# with open('./response.json', 'w', encoding='utf-8') as respFile:
	#	json.dump(response, respFile, ensure_ascii=False)

	#####	DELETING SESSION #####
	assistant.delete_session("d51d9cd1-7aae-4b79-a421-a3011081800e", "{}".format(sessionIdValue)).get_result()

	return response
####################################################################################################
@app.route('/api/speechtotext', methods=['POST'])
def speechtotext():
	authenticator = IAMAuthenticator('xO2J1yOR-WO7CaM8HpSTNp4IUkz1B9n9FV87WjVT0fyt')
	service = SpeechToTextV1(authenticator=authenticator)
	service.set_service_url('https://api.us-east.speech-to-text.watson.cloud.ibm.com/instances/ec264952-e773-4b45-84b1-a9d8ae6ccba5')

	# Lista modelos de reconhecimento de voz (idiomas, etc.)
	# models = service.list_models().get_result()
	# print(json.dumps(models, indent=2))

	# Selecionando o modelo pt-BR
	# model = service.get_model('pt-BR_Telephony').get_result()
	# print(json.dumps(model, indent=2))

	# Modelos pt-BR
	# pt-BR_BroadbandModel, pt-BR_NarrowbandModel, pt-BR_Telephony	
	
	# Speech-to-text do Watson
	sttResponse = service.recognize(
				audio=request.get_data(cache=False),
				content_type='audio/wav',
				model='pt-BR_Telephony',
				timestamps=True,
				word_confidence=True,
				smart_formatting=True
			).get_result()

	# Ask user to repeat if STT can't transcribe the speech
	if len(sttResponse['results']) < 1:
			return Response(mimetype='plain/text',
											response="")

	text_output = sttResponse['results'][0]['alternatives'][0]['transcript']
	text_output = text_output.strip()

	return Response(response=text_output, mimetype='plain/text')
####################################################################################################
@app.route('/api/texttospeech', methods=['POST'])
def texttospeech():
	authenticator = IAMAuthenticator('Zf7GD4i0Y1DhuhfKe-13cHJ-QTnpz8fjjweZ0Q6pODbY')
	service = TextToSpeechV1(authenticator=authenticator)
	service.set_service_url('https://api.us-east.text-to-speech.watson.cloud.ibm.com/instances/b57ffe19-93ef-4b10-b586-f7550e534fff')

	inputText = request.form.get('inputText')
	
	print(inputText)

	def generateTtsAudio():
		if inputText:

			response = service.synthesize(
				inputText, 
				accept='audio/wav',
				voice="pt-BR_IsabelaV3Voice").get_result()
			
			data = response.content
		
		return data

	# Converter data para base64
	encodedAudio = base64.b64encode(generateTtsAudio())
	response = "data:audio/wav;base64,"+str(encodedAudio,'ascii', 'ignore')

	return Response(response=response, mimetype='plain/text')
####################################################################################################

# Starts flask
if __name__ == '__main__':
  app.run(debug=True, host='127.0.0.1')