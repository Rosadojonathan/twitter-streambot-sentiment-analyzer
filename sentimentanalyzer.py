from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pydeepl

analyzer = SentimentIntensityAnalyzer()

# sentence = """
# Ticket master c’est de la merde Je viens d’acheter deux places pour Ed Sheeran j’ai reçu le mail de confirmation mais pas les places putain j’espère les recevoir parce que je ne claque pas 160€ pour rien moi
# """


def translate_to_french(func):
    def translate_sentence(sentence):
        translation = pydeepl.translate(sentence, "EN")
        #print("Original sentence :", sentence)
        #print("Translated Sentence :", translation)
        return translation
    return translate_sentence

def analyzeSentiment(sentence):
    snt = analyzer.polarity_scores(sentence)
    return snt

@translate_to_french
def get_sentence(sentence):
    return sentence

def sentimentAnalyzer(sentence):
    sentence = get_sentence(sentence)
    snt = analyzeSentiment(sentence)
    #print("\n Sentiments : {}".format(str(snt)))
    return snt


