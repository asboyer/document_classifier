Accuracy \
Accuracy increases as we get more documents to compare against
Accurary icreases with good manual classification
Accuracy increases with a clean document scan

Limitations \
There aren't that many documents to compare against
Most documents share very similar vocab, (ie. prescriptions, orders)
Time limitations because you have to do a little bit of manual classification and pattern recognition
Also time because turning large documents to text takes time and cost

Scalability is good, I think the more classifications that get made, the better and more accurate predictions can because

As that increases, I would weigh manual classification a little lower and tune the weight of automated predictions (hit rate, freq)

Inputs: unknown documents, known documents, manual mappings, common keywords
Outputs: classification, (under the hood more in depth debugging results)

Thought process:
assuming we already know these given documents belong to the categories given in the name

started off by looking through and making a "keywords" list for each category
    but then wanted to automate this process

text extraction was working for some pdfs, but not others

using tesseract takes a little longer to extract the text

originally made it a graph problem, built a graph for each document category \
each document is a vertex \
each edge is a keyword they share \
(later on added frequency and index location) \
then, was able to map shared keywords \

eventually ditched that because it became complicated but also lacked data to fully ruly on that classification \
    although it did do pretty well with compliance reports, because I suspect it had a lot of unqiue keywords

eventually just took an approach that was a hybrid between manual and automated, have manual mappings \
common keywords to ignore \
and an output of averages between keywords: \
raw keyword list:
```
    "compliance_report_4": {
        "last reset": {
            "count": 1,
            "order": 97
        }
    },
    "compliance_report_2": {
        "last reset": {
            "count": 1,
            "order": 121
        },
    }
```
averages between overall
```
    "last reset": {
        "avg_count": 1.0,
        "avg_order": 108.75,
        "hit_rate": 1.0
    }
```

# document_classifier
