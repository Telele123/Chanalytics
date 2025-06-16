#from cs50 import SQL
import random
from flask import Flask, render_template, request, session, redirect
from flask_session import Session
import matplotlib
matplotlib.use('Agg')  # Must come before importing pyplot
#matplotlib.use('TkAgg')  # or 'Qt5Agg' if you have PyQt installed
import matplotlib.pyplot as plt
import re
from collections import Counter
from datetime import datetime
import matplotlib.font_manager
for font in matplotlib.font_manager.fontManager.ttflist:
    if "Emoji" in font.name:
        print(font.name)
import emoji
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.tokenize import TweetTokenizer
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os

COLORS = ["#B0BAFF", "#9EA7F3", '#8C91DF', '#7D81C6', '#515882', '#323641', '#323651' ]
          




app = Flask(__name__)


app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
text_content = ""

if __name__ == "__main__":
    app.run(debug=True)


emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # Emoticons
        "\U0001F300-\U0001F5FF"  # Misc Symbols and Pictographs
        "\U0001F680-\U0001F6FF"  # Transport & Map
        "\U0001F700-\U0001F77F"  # Alchemical Symbols
        "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
        "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols, Symbols and Pictographs Extended-A
        "\U00002702-\U000027B0"  # Dingbats
        "\U000024C2-\U0001F251"  # Enclosed characters
        "]+", flags=re.UNICODE)


@app.route("/", methods=["GET", "POST"])
def index():
    """Home page and submit csv."""
    if request.method == "GET":
        session.clear()
        session['visited'] = False  

    if request.method == "POST":
        # Clear session data
        session.clear()  
        session['visited'] = True     
        # Get txt file
        file = request.files.get("txtfile")
        if not file or not file.filename.endswith(".txt"):
            return render_template("index.html", error="Please upload a valid .txt file.")


        if file and file.filename.endswith(".txt"):
            session['visited'] = True
            # Read file contents (as string)
            text_content = file.read().decode("utf-8")
            text_content = text_content.replace('\u200e', '')
            session['text_content'] = text_content
            # Do something with the text
            
            names = re.findall(r"\[\d{4}/\d{2}/\d{2}, \d{2}:\d{2}:\d{2}\] ([^:]+):", text_content)
            # Get the first two unique names
            unique_names = []
            for name in names:
                #name = name.strip()
                if name not in unique_names:
                    unique_names.append(name)
                if len(unique_names) == 2:
                    break
            

            # Store the names
            name1 = unique_names[0] if len(unique_names) > 0 else None
            name2 = unique_names[1] if len(unique_names) > 1 else None
            session['name1'] = name1
            session['name2'] = name2

            #Break down the text into messages for each user           
            pattern1 = (
                r"\[\d{4}/\d{2}/\d{2}, \d{2}:\d{2}:\d{2}\] "
                + re.escape(name1)
                + r": (.*?)(?=(?:\r?\n\[\d{4}/\d{2}/\d{2}, \d{2}:\d{2}:\d{2}\] .+?:)|\Z)"
            )

            pattern2 = (
                r"\[\d{4}/\d{2}/\d{2}, \d{2}:\d{2}:\d{2}\] "   # timestamp, e.g. [2025/06/04, 11:20:38]
                + re.escape(name2)                             # your name, e.g. Michelle
                + r": (.*?)"                                  # capture message text, non-greedy
                + r"(?=(?:\r?\n\[\d{4}/\d{2}/\d{2}, \d{2}:\d{2}:\d{2}\] .+?:)|\Z)"  # lookahead for next timestamp or end of text
            )
         

            oldlistofmessages1 = re.findall(pattern1, text_content, re.DOTALL)
            oldlistofmessages2 = re.findall(pattern2, text_content, re.DOTALL)

            print(f"NEW PATTERN: {re.findall(pattern1, text_content, re.DOTALL)}")
            print(f"NEW PATTERN2: {re.findall(pattern2, text_content, re.DOTALL)}")

            # Store the messages in session
            session['user1texts'] = oldlistofmessages1
            session['user2texts'] = oldlistofmessages2

            return render_template("index.html", success="File uploaded successfully!", text=text_content)
        
        else:
            return render_template("index.html", error="Please upload a valid .txt file.")
    
    return render_template("index.html")





@app.route('/messages', methods=["GET", "POST"])
def messages():
    if session.get('visited')== False:
        return render_template("index.html", error="Please upload a valid .txt file.")

    else:
        text_content = session.get('text_content')
        text_content = re.sub(emoji_pattern, '', text_content)
        text_content = text_content.replace('\u200e', '')  
        name1 = session.get('name1') if session.get('name1') else name1
        name2 = session.get('name2') if session.get('name2') else name2

        user1_texts = session.get('user1texts')
        user2_texts = session.get('user2texts')
        listofmessages1 = []
        listofmessages2 = []
        sumwords1 = 0
        sumwords2 = 0
        skip_phrases = [
            "Voice call", "No answer", "Missed voice call", "Tap to call back", "You deleted this message",
            "Audio omitted", "Sticker omitted", "Video omitted", "audio omitted", "video omitted", 
            "Video call", "Call failed, Try again", "Image omitted", "image omitted",
            "Messages and calls are end-to-end encrypted. Only people in this chat can read, listen to, or share them.",
        ]

        # Loop through all messages
        for msg in user1_texts:
            if any(phrase in msg for phrase in skip_phrases):
                continue # skip this message
            listofmessages1.append(msg)  # keep valid messages
        #Find number of words for each user        
            sumwords1 += len(re.findall(r'\w+', msg))

        for msg in user2_texts:
            if any(phrase in msg for phrase in skip_phrases):
                continue
            listofmessages2.append(msg)  # keep valid messages
            # Count words in this message and add to total
            sumwords2 += len(re.findall(r'\w+', msg))

        lenmessages1 = len(listofmessages1)
        lenmessage2 = len (listofmessages2)
        print(f"NEW COUTN MESSAGEES: {lenmessages1}")
        print(f"NEW SUM WORDS: {sumwords1}")
        
           
        #print(f"OLD COUNT MESSAGES {name1}:", countmessages1)

        #Find total number of messages
        countmessages = lenmessages1 + lenmessage2

        #Find percentage of messages for each user
        percentage1 = (lenmessages1 / countmessages) * 100 if countmessages > 0 else 0
        percentage2 = (lenmessage2 / countmessages) * 100 if countmessages > 0 else 0
        
        print(percentage1, percentage2)
        print(f"Total messages:", countmessages)

        # Create a pie chart of text percentage distribution
        if countmessages > 0:
            labels = [name1, name2]         # Names like ['Michelle', 'Ruan']
            sizes = [percentage1, percentage2]  # Percentages like [60.0, 40.0]
            print(f"Labels: {labels}")
            print(f"Sizes: {sizes}")
            colors = ['#DD5D71', '#6FB9D7']
            #explode = (0.1, 0)
            plt.figure(figsize=(10, 10))
            plt.pie(sizes, labels=labels, colors=colors,
                    autopct='%1.1f%%', startangle=140)
            plt.axis('equal')
            plt.title('Text Distribution')
            plt.savefig('static/pie_chart.png')
        
        #Create a pie chart of word percentage distribution
        if lenmessages1 + lenmessage2 > 0:
            percentage1ofwords = (sumwords1 / (sumwords1+sumwords2)) * 100 if (countmessages) > 0 else 0
            percentage2ofwords = (sumwords2 / (sumwords1+sumwords2)) * 100 if (countmessages) > 0 else 0
            labels = [name1, name2]         # Names like ['Michelle', 'Ruan']
            sizes = [percentage1ofwords, percentage2ofwords]  # Percentages like [60.0, 40.0]
            print(f"Labels: {labels}")
            print(f"Sizes: {sizes}")
            colors = ['#DD5D71', '#6FB9D7']
            #explode = (0.1, 0)
            plt.figure(figsize=(10, 10))
            plt.pie(sizes, labels=labels, colors=colors,
                    autopct='%1.1f%%', startangle=140)
            plt.axis('equal')
            plt.title('Word Distribution')
            plt.savefig('static/pie_chart_words.png')
            plt.close()

        #Find first text message
        first_message = listofmessages1[0] if listofmessages1 else None
        second_message = listofmessages2[0] if listofmessages2 else None

        #Find first and last timestamp
        timestamplist = re.findall(r"\[(\d{4}/\d{2}/\d{2})", text_content)
        datelist = [datetime.strptime(date, "%Y/%m/%d") for date in timestamplist]
        if datelist:
            first_timestamp = min(datelist)
            last_timestamp = max(datelist)
        days_passed = (last_timestamp - first_timestamp).days

        # Render the template with the data
        return render_template('messages.html', name1=name1, name2=name2, 
                            countmessages1=lenmessages1, countmessages2=lenmessage2, 
                            percentage1=percentage1, percentage2=percentage2,
                            countmessages=countmessages, first_message=first_message, second_message=second_message
                            ,first_timestamp=first_timestamp, last_timestamp=last_timestamp, days_passed=days_passed,
                            countwords1=sumwords1, countwords2=sumwords2)



@app.route('/emojis', methods=["GET", "POST"])
def emojis():
        if session.get('visited')== False:
            return render_template("index.html", error="Please upload a valid .txt file.")

        text_content = session.get('text_content')
        emojislist = emoji_pattern.findall(text_content)
        name1 = session.get('name1')
        name2 = session.get('name2')
        user1texts = session.get('user1texts')
        user2texts = session.get('user2texts')

        newemojis = []
        for e in emoji.emoji_list(text_content):
            newemojis.append (e['emoji'])

        #Count the occurrences of each emoji
        emoji_counts = Counter(newemojis)

        print(f"Emoji counts: {emoji_counts}")
        print(f"New emojis: {newemojis}")
        print(f"Emojis list: {emojislist}")
        
        # Sort emojis by frequency
        sorted_emojis = emoji_counts.most_common(10) 

        print(f"Sorted emojis: {sorted_emojis}")

        #Word cloud for emojis
        top50emojis = dict(Counter(newemojis).most_common(50))  # convert to dict
        emoji_wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(top50emojis)
        # Save emoji wordcloud image to static folder
        emoji_image_path = os.path.join('static', 'emoji_wordcloud.png')
        emoji_wordcloud.to_file(emoji_image_path)

        #Pie chart of emoji distribution
        if (sorted_emojis):
            labels = [str(i) for i in range(1, len(sorted_emojis)+1)] 
            sizes = [count for emoji, count in sorted_emojis]
            colors = ['#C7D8EC', '#ADC6E5', '#8CB1DD', '#5B9BD5', '#538EC3', '#497fB0', '#3F6D97', 
                      "#3D6284", "#364F67", "#242F39"]
            plt.figure(figsize=(10, 10))
            plt.pie(sizes, colors=colors,
                    autopct='%1.1f%%', startangle=140)
            plt.axis('equal')
            plt.title('Emoji Distribution')
            plt.savefig('static/emoji_pie_chart.png', transparent=True)
            plt.close()
        else:
            sorted_emojis = []

        # Number of unique emojis
        unique_emojis = len(emoji_counts)
        print(f"Unique emojis: {unique_emojis}")
        
        #Person 1 top emoji    
        emojisuser1 = []
        combined_text1 = ' '.join(user1texts)
        for e in emoji.emoji_list(combined_text1):
            emojisuser1.append(e['emoji'])
        counter1 = Counter(emojisuser1)
        person1_top_emoji = (counter1.most_common(1))[0] if counter1 else None
        #person1_emojis = ' '.join(user1texts)
        #person1_emoji_counts = Counter(emoji_pattern.findall(person1_emojis))

     
        #Person 2 top emoji
        emojisuser2 = []
        combined_text2 = ' '.join(user2texts)
        for e in emoji.emoji_list(combined_text2):
            emojisuser2.append(e['emoji'])
        counter2 = Counter(emojisuser2)
        print(f"Counter2: {counter2}")
        print(f"Emojisuser2: {emojisuser2}")
        person2_top_emoji = (counter2.most_common(1))[0] if counter2 else None
        #person2_emojis = ' '.join(user2texts)
        #person2_emoji_counts = Counter(emoji_pattern.findall(person2_emojis))
        #person2_top_emoji = person2_emoji_counts.most_common(1)[0] if person2_emoji_counts else None



        #Search option
        if request.method=="POST":
            selected_emoji = request.form.get('emoji')
            if emoji_pattern.fullmatch(selected_emoji) and selected_emoji:
                countofemoji = text_content.count(selected_emoji)
                countperson1ofemoji = combined_text1.count(selected_emoji)
                countperson2ofemoji = combined_text2.count(selected_emoji)
                return render_template('emojis.html', name1 = name1, name2 = name2, sorted_emojis=sorted_emojis,
                                unique_emojis=unique_emojis, 
                                 person1_top_emoji=person1_top_emoji, 
                                 person2_top_emoji=person2_top_emoji,
                                 countofemoji=countofemoji if 'countofemoji' in locals() else None,
                                 countperson1ofemoji=countperson1ofemoji if 'countperson1ofemoji' in locals() else None,
                                 countperson2ofemoji=countperson2ofemoji if 'countperson2ofemoji' in locals() else None,
                                 selected_emoji=selected_emoji)
            
            else:
                return render_template('emojis.html', name1 = name1, name2 = name2, sorted_emojis=sorted_emojis,
                                unique_emojis=unique_emojis, 
                                 person1_top_emoji=person1_top_emoji, 
                                 person2_top_emoji=person2_top_emoji,
                                error="Not an emoji.")
    
            
        return render_template('emojis.html', name1 = name1, name2 = name2, sorted_emojis=sorted_emojis,
                                 unique_emojis=unique_emojis,
                                 person1_top_emoji=person1_top_emoji, 
                                 person2_top_emoji=person2_top_emoji,
                                 countofemoji=countofemoji if 'countofemoji' in locals() else None,
                                 countperson1ofemoji=countperson1ofemoji if 'countperson1ofemoji' in locals() else None,
                                 countperson2ofemoji=countperson2ofemoji if 'countperson2ofemoji' in locals() else None)





@app.route('/words', methods=["GET", "POST"])
def words():
    if session.get('visited')== False:
        return render_template("index.html", error="Please upload a valid .txt file.")

    text_content = session.get('text_content')
    name1 = session.get('name1')
    name2 = session.get('name2')
    user1texts = session.get('user1texts')
    user2texts = session.get('user2texts')

    skip_phrases = [
            "Voice call", "No answer", "Missed voice call", "Tap to call back", "You deleted this message",
            "Audio omitted", "Sticker omitted", "Video omitted", "audio omitted", "video omitted", 
            "Video call", "Call failed, Try again", "Image omitted", "image omitted",
            "Messages and calls are end-to-end encrypted. Only people in this chat can read, listen to, or share them.",
        ]

    # Loop through all messages
    listofmessages1 = []
    for msg in user1texts:
        if any(phrase in msg for phrase in skip_phrases):
            continue # skip this message
        listofmessages1.append(msg)  # keep valid messages
    listofmessages2 = []
    for msg in user2texts:
        if any(phrase in msg for phrase in skip_phrases):
            continue
        listofmessages2.append(msg)

    #Find top 10 words
    combined_text1 = ' '.join(listofmessages1)
    combined_text2 = ' '.join(listofmessages2)
    all_words = combined_text1 + ' ' + combined_text2

    tokenizer = TweetTokenizer(preserve_case=False)
    tokens1 = tokenizer.tokenize(combined_text1)
    tokens2 = tokenizer.tokenize(combined_text2)
    alltokens = tokenizer.tokenize(all_words)

    # Filter out non-alphabetic tokens
    alpha1 = [w for w in tokens1 if w.isalpha()]
    alpha2 = [w for w in tokens2 if w.isalpha()]
    allalpha = [w for w in alltokens if w.isalpha()]

    #Filter out stop words
    stop_words = set(stopwords.words('english'))
    filtered1 = [w for w in alpha1 if w not in stop_words]
    filtered2 = [w for w in alpha2 if w not in stop_words]
    all_filtered = [w for w in allalpha if w not in stop_words]
    counts1 = Counter(filtered1)
    counts2 = Counter(filtered2)

    word_counts1 = counts1.most_common(10)  #Get the 10 most common words for user 1    
    word_counts2 = counts2.most_common(10)  #Get the 10 most common words for user 2

    #Top 10 words for everyone
    top10words = Counter(all_filtered).most_common(10)

        ## WhatsApp green background and white text
    WA_GREEN = '#1A8754'
    WHITE = '#FFFFFF'

    # Custom color function for white text
    def white_color_func(*args, **kwargs):
        return WHITE

    # Word cloud for everyone
    top50words = dict(Counter(all_filtered).most_common(50))
    wordcloud = WordCloud(
        width=400,
        height=200,
        background_color=WA_GREEN,
        color_func=white_color_func
    ).generate_from_frequencies(top50words)

    # Word cloud for User 1
    top50words1 = dict(Counter(filtered1).most_common(50))
    wordcloud1 = WordCloud(
        width=400,
        height=200,
        background_color=WA_GREEN,
        color_func=white_color_func
    ).generate_from_frequencies(top50words1)

    # Word cloud for User 2
    top50words2 = dict(Counter(filtered2).most_common(50))
    wordcloud2 = WordCloud(
        width=400,
        height=200,
        background_color=WA_GREEN,
        color_func=white_color_func
    ).generate_from_frequencies(top50words2)


    # Save wordcloud image to static folder
    image_path = os.path.join('static', 'wordcloud.png')
    wordcloud.to_file(image_path)
    image_path1 = os.path.join('static', 'wordcloud1.png')
    wordcloud1.to_file(image_path1)
    image_path2 = os.path.join('static', 'wordcloud2.png')
    wordcloud2.to_file(image_path2)

    #Unique words
    unique_words = set(allalpha)
    unique_words_count = len(unique_words)
    
    search_word = None
    search1 = None
    search2 = None
    # Search option
    if request.method == "POST":
        search_word = request.form.get('search_word')
        if search_word:
            search1 = sum(1 for word in filtered1 if word.lower() == search_word.lower())
            search2 = sum(1 for word in filtered2 if word.lower() == search_word.lower())
            return render_template('words.html', name1=name1, name2=name2,
                                   word_counts1=word_counts1, word_counts2=word_counts2,
                                   search_word=search_word, top10words=top10words,
                                    search1=search1,
                                    search2=search2,
                                   unique_words_count=unique_words_count)
                                
    
    return render_template('words.html', name1=name1, name2=name2,
                                   word_counts1=word_counts1, word_counts2=word_counts2,
                                   search_word=search_word, top10words=top10words,
                                    search1=search1,
                                    search2=search2,
                                   unique_words_count=unique_words_count)
                                


@app.route('/links')
def links():
    if session.get('visited')== False:
        return render_template("index.html", error="Please upload a valid .txt file.")

    text_content = session.get('text_content')
    name1 = session.get('name1')
    name2 = session.get('name2')
    user1texts = session.get('user1texts')
    user2texts = session.get('user2texts')
    text = user1texts + user2texts
    
    countvoicecalls = 0
    countvideocalls = 0
    countaudio = 0
    durationofvoicecalls = 0
    durationofvideocalls = 0
    countimages = 0
    countvideos = 0
    countlinks = 0


    for msg in text:
        #IMAGES
        if "image omitted" == msg:
            countimages += 1
        #VOICE CALLS
        if "Voice call" in msg:
            countvoicecalls += 1
            durationmin = int (re.search(r'(\d+) min', msg).group(1)) if re.search(r'(\d+) min', msg) else 0
            durationhr = int (re.search(r'(\d+) hr', msg).group(1)) if re.search(r'(\d+) hr', msg) else 0
            durationsec = int (re.search(r'(\d+) sec', msg).group(1)) if re.search(r'(\d+) sec', msg) else 0
            print (re.search(r'(\d+) min', msg))
            print(re.search(r'(\d+) hr', msg))
            print(re.search(r'(\d+) sec', msg))
            duration = durationmin + (durationhr * 60) + (durationsec / 60)
            durationofvoicecalls += duration
        #VIDEO CALLS
        if "Video call" in msg:
            countvideocalls += 1
            durationmin = int (re.search(r'(\d+) min', msg).group(1)) if re.search(r'(\d+) min', msg) else 0
            durationhr = int (re.search(r'(\d+) hr', msg).group (1)) if re.search(r'(\d+) hr', msg) else 0
            durationsec = int (re.search(r'(\d+) sec', msg).group(1)) if re.search(r'(\d+) sec', msg) else 0
            duration = durationmin + (durationhr * 60 if durationhr else 0) + (durationsec / 60 if durationsec else 0)
            durationofvideocalls += duration
        #AUDIO
        if "audio omitted" == msg:
            countaudio += 1
        #VIDEOS
        if "video omitted" == msg:
            countvideos += 1
        #LINKS
        if "https://" in msg or "http://" in msg:
            countlinks += 1
            print(f"Link found: {msg}")  # Debugging line to see found links

    return render_template('links.html', name1=name1, name2=name2, 
                            countimages = countimages,
                            countvoicecalls=countvoicecalls, 
                            durationofvoicecalls=durationofvoicecalls,
                            countvideocalls=countvideocalls, 
                            durationofvideocalls=durationofvideocalls,
                            countaudio=countaudio, 
                            countvideos=countvideos, countlinks=countlinks)



@app.route('/timeline')
def timeline():
    text_content = session.get('text_content')

    timestamplist = re.findall(r"\[\d{4}/\d{2}/\d{2}, \d{2}:\d{2}:\d{2}\]", text_content)
    print (timestamplist)
    datetimes = [
        datetime.strptime(ts[1:-1], "%Y/%m/%d, %H:%M:%S")
        for ts in timestamplist]
    hours = [dt.hour for dt in datetimes]
    days = [dt.date().isoformat() for dt in datetimes]
    weekdays = [dt.strftime("%A") for dt in datetimes]
    month = [dt.strftime("%B") for dt in datetimes]

    print (datetimes)

    mostcommonhour = Counter (hours)
    mostcommondays = Counter (days)
    mostcommonweekday = Counter(weekdays)
    mostcommonmonth = Counter(month)

    tophour = mostcommonhour.most_common(1)[0] if mostcommonhour else None
    topday = mostcommondays.most_common(1)[0] if mostcommondays else None
    topweekday = mostcommonweekday.most_common(1)[0] if mostcommonweekday else None

    # Create a bar chart for most common hours
    plt.figure(figsize=(10, 6))
    plt.bar(mostcommonhour.keys(), mostcommonhour.values(), color= '#1A8754')
    plt.xlabel('Hour of the Day')
    plt.ylabel('Number of Messages')
    plt.title('Most Common Hours of Messages')
    plt.xticks(range(24))  # Ensure all hours are shown
    plt.savefig('static/most_common_hours.png')

    #Create a pie chart for most common days
    plt.figure(figsize=(8, 6))
    colors = ['#C7D8EC', '#ADC6E5', '#8CB1DD', '#5B9BD5', '#538EC3', '#497fB0', '#3F6D97', 
                      "#3D6284", "#364F67", "#242F39"]
    plt.pie(mostcommonweekday.values(), colors=colors, labels=mostcommonweekday.keys(), autopct='%1.1f%%', startangle=140)
    plt.title('Most Common Days of Messages')
    plt.savefig('static/most_common_days.png')

    #Create a bar chart of most common months
    plt.figure(figsize=(10, 6))
    plt.bar(mostcommonmonth.keys(), mostcommonmonth.values(), color= '#1A8754')
    plt.xlabel('Month')
    plt.ylabel('Number of Messages')
    plt.title('Most Common Months of Messages')
    plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
    plt.savefig('static/most_common_months.png')

    return render_template('timeline.html', tophour=tophour, topday=topday, topweekday=topweekday)
                           



