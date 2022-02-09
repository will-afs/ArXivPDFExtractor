# import pandas as pd
# from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
# import spacy
# from spacy.lang.en.examples import sentences 

# import nltk
# from nltk.tag.stanford import StanfordNERTagger as NERTagger

# import spacy
# from spacy import displacy
# from collections import Counter
    
    # # Bag of words

    # #sentence_1="This is a good job.I will not miss it for anything"
    # #sentence_2="This is not good at all"

    # CountVec = CountVectorizer(ngram_range=(1,1), # to use bigrams ngram_range=(2,2)
    #                         stop_words='english')
    # #transform
    # #Count_data = CountVec.fit_transform([sentence_1,sentence_2])
    # Count_data = CountVec.fit_transform([pdf_content])

    # #create dataframe
    # cv_dataframe=pd.DataFrame(Count_data.toarray(),columns=CountVec.get_feature_names())
    # print(cv_dataframe)


    # st = NERTagger('fil-rouge/stanford-ner/english.all.3class.distsim.crf.ser.gz', 'fil-rouge//stanford-ner/stanford-ner.jar')
    # text = pdf_content

    # for sent in nltk.sent_tokenize(text):
    #     tokens = nltk.tokenize.word_tokenize(sent)
    #     tags = st.tag(tokens)
    #     for tag in tags:
    #         if tag[1]=='PERSON': print(tag)


    # nlp = spacy.load("en_core_web_sm")
    # doc = nlp(sentences[0])
    # print(doc.text)
    # for token in doc:
    #     print(token.text, token.pos_, token.dep_)


    # nlp = spacy.load("en_core_web_sm")
    # from pprint import pprint
    # nlp = en_core_web_sm.load()

# pip install spacy 
# import spacy 
# nlp = spacy.load("en_core_web_sm")
# text = "Apple acquired Zoom in China on Wednesday 6th May 2020. This news has made Apple and Google stock jump by 5% on Dow Jones Index in the United States of America"
# def spacylist(text, nlp):
    
#     doc = nlp(text)
#     entities = []
#     for ent in doc.ents:
#         if ent.label_ == "PERSON": 
#           entities.append(ent.text)
#     return entities


# # PDF TO TEXT

# from PyPDF2 import PdfFileReader
# import pdftotext

# # Extracting meta data
# with open("new_file.pdf", "rb") as file:
#     data = pdftotext.PDF(file)
#     pdf = PdfFileReader(file)
#     info = pdf.getDocumentInfo()
#     number_of_pages = pdf.getNumPages()
#     author = info.author
#     creator = info.creator
#     producer = info.producer
#     subject = info.subject
#     title = info.title

# doc = nlp('European authorities fined Google a record $5.1 billion on Wednesday for abusing its power in the mobile phone market and ordered the company to alter its practices')
# pprint([(X.text, X.label_) for X in doc.ents])

# pprint([(X, X.ent_iob_, X.ent_type_) for X in doc])

# article = nlp(pdf_content)
# len(article.ents)

# labels = [x.label_ for x in article.ents]
# Counter(labels)

# items = [x.text for x in article.ents]
# Counter(items).most_common(3)

# sentences = [x for x in article.sents]
# print(sentences[20])

# displacy.render(nlp(str(sentences[20])), jupyter=True, style='ent')

# displacy.render(nlp(str(sentences)), style='dep', jupyter = True, options = {'distance': 120})

# [(x.orth_,x.pos_, x.lemma_) for x in [y 
#                                       for y
#                                       in nlp(str(sentences)) 
#                                       if not y.is_stop and y.pos_ != 'PUNCT']]

# dict([(str(x), x.label_) for x in nlp(str(sentences)).ents])

# print([(x, x.ent_iob_, x.ent_type_) for x in sentences[20]])

# displacy.render(article, jupyter=True, style='ent')




# print("Info:", info)
# print("Pages count:", number_of_pages)
# print("Author:", author)
# print("Creator:", creator)
# print("Producer:", producer)
# print("Subject:", subject)
# print("Title:", title)
# pdf_content = "\n".join(data)
# print("Content:", pdf_content)