from flask import Flask,url_for,request,render_template,jsonify,send_file
from flask_bootstrap import Bootstrap
import json
import extract
import highlight
import conversionpackages
from werkzeug.utils import secure_filename
# NLP Pkgs
import spacy
from textblob import TextBlob 
nlp = spacy.load('en_core_web_sm')

# WordCloud & Matplotlib Packages
from wordcloud import WordCloud
import matplotlib.pyplot as plt 
from io import BytesIO
import random
import time
import notable
from cdqa.utils.filters import filter_paragraphs
from cdqa.utils.download import download_model, download_bnpp_data
from cdqa.pipeline.cdqa_sklearn import QAPipeline
from pdf_reading import *


UPLOAD_FOLDER = "/home/sam/Desktop/new_summarizer/uplaod"
rawtext=''''''

# Initialize App
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER #check
Bootstrap(app)

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/doc')
def doc():
	return render_template('doc.html')


@app.route('/ask',methods=['POST'])
def ask():
    name = request.form['btn-input']
    
    #print(name)    
    f=open('current.txt')
    file1=f.read().rstrip()
    f.close()
    cdqa_pipeline = QAPipeline(reader='models/bert_qa_vCPU-sklearn.joblib')
    row=file_open(file1)
    df=pd.DataFrame(row)
    df=df.T
    df.columns=['title','paragraphs']
#print(df.head())
# Fitting the retriever to the list of documents in the dataframe
    cdqa_pipeline.fit_retriever(df)
    prediction = cdqa_pipeline.predict(name)
    ret=[name,prediction[0],prediction[1],prediction[2]]
    speech = ret[1]+"\n\n Related Paragraph"+ret[3]
    print('This is error output', speech)
    #return speech
    return render_template('index.html', value1=name, value2=speech)

@app.route('/analyze',methods=['GET','POST'])
def analyze():
	start = time.time()
	# Receives the input query from form
	if request.method == 'POST':
		'''global rawtext
		global phrases
		global important
		global bold'''

		rawtext = request.form['rawtext']
		notable1 = notable.notable(rawtext)
		notable1 = list(set(notable1))
		conversionpackages.text2pdf(rawtext)
		phrases = conversionpackages.getImpPhrases()
		docx = nlp(rawtext)
		initial="""
		<html>
		<head>
		<title>Text Highlighted</title>
		<style>
			a { color: #ff6600; transition: .5s; -moz-transition: .5s; -webkit-transition: .5s; -o-transition: .5s; font-family: 'Muli', sans-serif; }


a:hover { text-decoration: underline }


h1 { padding-bottom: 15px }


h1 a { font-family: 'Open Sans Condensed', sans-serif; font-size: 48px; color: #333; }


h1 a:hover { color: #ff6600; text-decoration: none; }


p { color: #333; font-family: 'Muli', sans-serif; margin-bottom: 15px; }


a.more-link { color: white; font-weight: bold; font-size: 14px; font-family: Arial, Helvetica, sans-serif; padding: 3px 10px; background-color: #ff6600; border-radius: 5px; float: right; }


a.more-link:hover { text-decoration: none; background-color: #666; border-radius: 0px; }
		</style>
		</head>
		<body>
		<p>"""
		#towrite=initial+text+"""</p></body></html"""
		#f=open('templates/doc.html','w',encoding="utf8")
		#f.write(towrite)
		#f.close()
		#print(text)
		#f=open('text.txt','w')
		#f.write(rawtext)
		#f.close()
		# Word Info
		custom_wordinfo = [(token.text,token.lemma_,token.shape_,token.is_alpha,token.is_stop) for token in docx ]
		custom_postagging = [(word.text,word.tag_,word.pos_,word.dep_) for word in docx]
		# NER
		custom_namedentities = [(entity.text,entity.label_)for entity in docx.ents]
		blob = TextBlob(rawtext)
		blob_sentiment,blob_subjectivity = blob.sentiment.polarity ,blob.sentiment.subjectivity
		# allData = ['Token:{},Tag:{},POS:{},Dependency:{},Lemma:{},Shape:{},Alpha:{},IsStopword:{}'.format(token.text,token.tag_,token.pos_,token.dep_,token.lemma_,token.shape_,token.is_alpha,token.is_stop) for token in docx ]
		allData = [('"Token":"{}","Tag":"{}","POS":"{}","Dependency":"{}","Lemma":"{}","Shape":"{}","Alpha":"{}","IsStopword":"{}"'.format(token.text,token.tag_,token.pos_,token.dep_,token.lemma_,token.shape_,token.is_alpha,token.is_stop)) for token in docx ]

		result_json = json.dumps(allData, sort_keys = False, indent = 2)

		end = time.time()
		final_time = end-start

		conversionpackages.Outputpdf()
	return render_template('index.html',ctext=rawtext, custom_postagging=notable1,custom_tokens=phrases,blob_subjectivity=blob_subjectivity,final_time=final_time,result_json=result_json)

@app.route('/analyze2',methods=['POST'])
def analyze2():
	start = time.time()
	# ALLOWED_EXTENSIONS = {'txt', 'pdf'}
	file = request.files['file'] # check assuming it is path
	#file.save(file.filename)
	f69="input.pdf"
	file.save(secure_filename(f69))
	conversionpackages.Outputpdf()


	rawtext = conversionpackages.pdftotext()
	notable1 = notable.notable(rawtext)
	notable1 = list(set(notable1))
	conversionpackages.text2pdf(rawtext)
	phrases = conversionpackages.getImpPhrases()
	docx = nlp(rawtext)
	initial="""
	<html>
	<head>
	<title>Text Highlighted</title>
	<style>
		a { color: #ff6600; transition: .5s; -moz-transition: .5s; -webkit-transition: .5s; -o-transition: .5s; font-family: 'Muli', sans-serif; }


a:hover { text-decoration: underline }


h1 { padding-bottom: 15px }


h1 a { font-family: 'Open Sans Condensed', sans-serif; font-size: 48px; color: #333; }


h1 a:hover { color: #ff6600; text-decoration: none; }


p { color: #333; font-family: 'Muli', sans-serif; margin-bottom: 15px; }


a.more-link { color: white; font-weight: bold; font-size: 14px; font-family: Arial, Helvetica, sans-serif; padding: 3px 10px; background-color: #ff6600; border-radius: 5px; float: right; }


a.more-link:hover { text-decoration: none; background-color: #666; border-radius: 0px; }
	</style>
	</head>
	<body>
	<p>"""
	#towrite=initial+text+"""</p></body></html"""
	#f=open('templates/doc.html','w',encoding="utf8")
	#f.write(towrite)
	#f.close()
	#print(text)
	#f=open('text.txt','w')
	#f.write(rawtext)
	#f.close()
	# Word Info
	custom_wordinfo = [(token.text,token.lemma_,token.shape_,token.is_alpha,token.is_stop) for token in docx ]
	custom_postagging = [(word.text,word.tag_,word.pos_,word.dep_) for word in docx]
	# NER
	custom_namedentities = [(entity.text,entity.label_)for entity in docx.ents]
	blob = TextBlob(rawtext)
	blob_sentiment,blob_subjectivity = blob.sentiment.polarity ,blob.sentiment.subjectivity
	# allData = ['Token:{},Tag:{},POS:{},Dependency:{},Lemma:{},Shape:{},Alpha:{},IsStopword:{}'.format(token.text,token.tag_,token.pos_,token.dep_,token.lemma_,token.shape_,token.is_alpha,token.is_stop) for token in docx ]
	allData = [('"Token":"{}","Tag":"{}","POS":"{}","Dependency":"{}","Lemma":"{}","Shape":"{}","Alpha":"{}","IsStopword":"{}"'.format(token.text,token.tag_,token.pos_,token.dep_,token.lemma_,token.shape_,token.is_alpha,token.is_stop)) for token in docx ]

	result_json = json.dumps(allData, sort_keys = False, indent = 2)

	end = time.time()
	final_time = end-start
	return render_template('index.html',ctext=rawtext,custom_tokens=phrases,custom_postagging=notable1,blob_subjectivity=blob_subjectivity,final_time=final_time,result_json=result_json)

	# Analysis
	
@app.route('/analyze1',methods=['POST'])
def analyze1():
	
	url = request.form['url']
	conversionpackages.urltopdf(url)
	conversionpackages.Outputpdf()

	return "success"
# 	rawtext = conversionpackages.pdftotext()
# 	# Analysis
# 	docx = nlp(rawtext)
# 	phrases=extract.phrases(rawtext)
	
# 	important=extract.important(rawtext)
# 	important=list(set(important))
# 	bold=extract.bold(rawtext)
# 	bold=list(set(bold))
# 	# Tokens
# 	custom_tokens = [token.text for token in docx ]
# 	#print(custom_tokens)
# 	#print(bold)
# 	#print(important)
# 	#print('\n\n')
# 	#print(phrases)
# 	text=highlight.highlight(rawtext,phrases,bold,important)
# 	print(text)

# 	initial="""
# 	<html>
# 	<head>
# 	<title>Text Highlighted</title>
# 	<style>
# 		a { color: #ff6600; transition: .5s; -moz-transition: .5s; -webkit-transition: .5s; -o-transition: .5s; font-family: 'Muli', sans-serif; }


# a:hover { text-decoration: underline }


# h1 { padding-bottom: 15px }


# h1 a { font-family: 'Open Sans Condensed', sans-serif; font-size: 48px; color: #333; }


# h1 a:hover { color: #ff6600; text-decoration: none; }


# p { color: #333; font-family: 'Muli', sans-serif; margin-bottom: 15px; }


# a.more-link { color: white; font-weight: bold; font-size: 14px; font-family: Arial, Helvetica, sans-serif; padding: 3px 10px; background-color: #ff6600; border-radius: 5px; float: right; }


# a.more-link:hover { text-decoration: none; background-color: #666; border-radius: 0px; }
# 	</style>
# 	</head>
# 	<body>
# 	<p>"""
# 	towrite=initial+text+"""</p></body></html"""
# 	f=open('templates/doc.html','w',encoding="utf8")
# 	f.write(towrite)
# 	f.close()
# 	print(text)
# 	f=open('text.txt','w')
# 	f.write(rawtext)
# 	f.close()
# 	# Word Info
# 	custom_wordinfo = [(token.text,token.lemma_,token.shape_,token.is_alpha,token.is_stop) for token in docx ]
# 	custom_postagging = [(word.text,word.tag_,word.pos_,word.dep_) for word in docx]
# 	# NER
# 	custom_namedentities = [(entity.text,entity.label_)for entity in docx.ents]
# 	blob = TextBlob(rawtext)
# 	blob_sentiment,blob_subjectivity = blob.sentiment.polarity ,blob.sentiment.subjectivity
# 	# allData = ['Token:{},Tag:{},POS:{},Dependency:{},Lemma:{},Shape:{},Alpha:{},IsStopword:{}'.format(token.text,token.tag_,token.pos_,token.dep_,token.lemma_,token.shape_,token.is_alpha,token.is_stop) for token in docx ]
# 	allData = [('"Token":"{}","Tag":"{}","POS":"{}","Dependency":"{}","Lemma":"{}","Shape":"{}","Alpha":"{}","IsStopword":"{}"'.format(token.text,token.tag_,token.pos_,token.dep_,token.lemma_,token.shape_,token.is_alpha,token.is_stop)) for token in docx ]

# 	result_json = json.dumps(allData, sort_keys = False, indent = 2)

# 	end = time.time()
# 	final_time = end-start
# 	return render_template('index.html',ctext=rawtext,custom_tokens=phrases,custom_postagging=bold,custom_namedentities=important,custom_wordinfo=text,blob_sentiment=bold,blob_subjectivity=blob_subjectivity,final_time=final_time,result_json=result_json)

@app.route('/download')
def download_file():
	#path = "html2pdf.pdf"
	#path = "info.xlsx"
	path = "output.pdf"
	#path = "sample.txt"
	return send_file(path, as_attachment=True)


# API ROUTES
@app.route('/api')
def basic_api():
	return render_template('restfulapidocs.html')

# API FOR TOKENS
@app.route('/api/tokens/<string:mytext>',methods=['GET'])
def api_tokens(mytext):
	# Analysis
	docx = nlp(mytext)
	# Tokens
	mytokens = [token.text for token in docx ]
	return jsonify(mytext,mytokens)

# API FOR LEMMA
@app.route('/api/lemma/<string:mytext>',methods=['GET'])
def api_lemma(mytext):
	# Analysis
	docx = nlp(mytext.strip())
	# Tokens & Lemma
	mylemma = [('Token:{},Lemma:{}'.format(token.text,token.lemma_))for token in docx ]
	return jsonify(mytext,mylemma)

# API FOR NAMED ENTITY
@app.route('/api/ner/<string:mytext>',methods=['GET'])
def api_ner(mytext):
	# Analysis
	docx = nlp(mytext)
	# Tokens
	mynamedentities = [(entity.text,entity.label_)for entity in docx.ents]
	return jsonify(mytext,mynamedentities)

# API FOR NAMED ENTITY
@app.route('/api/entities/<string:mytext>',methods=['GET'])
def api_entities(mytext):
	# Analysis
	docx = nlp(mytext)
	# Tokens
	mynamedentities = [(entity.text,entity.label_)for entity in docx.ents]
	#mynamedentities=[]
	return jsonify(mytext,mynamedentities)


# API FOR SENTIMENT ANALYSIS
@app.route('/api/sentiment/<string:mytext>',methods=['GET'])
def api_sentiment(mytext):
	# Analysis
	blob = TextBlob(mytext)
	mysentiment = [ mytext,blob.words,blob.sentiment ]
	return jsonify(mysentiment)

# API FOR MORE WORD ANALYSIS
@app.route('/api/nlpiffy/<string:mytext>',methods=['GET'])
def nlpifyapi(mytext):

	docx = nlp(mytext.strip())
	allData = ['Token:{},Tag:{},POS:{},Dependency:{},Lemma:{},Shape:{},Alpha:{},IsStopword:{}'.format(token.text,token.tag_,token.pos_,token.dep_,token.lemma_,token.shape_,token.is_alpha,token.is_stop) for token in docx ]
	
	return jsonify(mytext,allData)
	

# IMAGE WORDCLOUD
@app.route('/images')
def imagescloud():
    return "Enter text into url eg. /fig/yourtext "


@app.route('/images/<mytext>')
def images(mytext):
    return render_template("index.html", title=mytext)

@app.route('/fig/<string:mytext>')
def fig(mytext):
    plt.figure(figsize=(20,10))
    wordcloud = WordCloud(background_color='white', mode = "RGB", width = 2000, height = 1000).generate(mytext)
    plt.imshow(wordcloud)
    plt.axis("off")
    img = BytesIO()
    plt.savefig(img)
    img.seek(0)
    return send_file(img, mimetype='image/png')


@app.route('/about')
def about():
	return render_template('about.html')

if __name__ == '__main__':
	app.run(debug=True)
