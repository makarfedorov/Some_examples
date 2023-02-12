from flask import Flask, request, render_template, send_file, redirect, url_for
import xml.etree.ElementTree as ET
import io
import xml.dom.minidom


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_xml', methods=['POST'])
def create_xml():
    # Get user input
    title = request.form['title']
    author = request.form['author']
    date = request.form['date']

    # Validate the user input
    errors = []
    if not title:
        errors.append("title is required")
    if not author:
        errors.append("author is required")
    if not date:
        errors.append("date is required")
    if errors:
        return render_template('index.html', title=title if not "title is required" in errors else "", author=author if not "author is required" in errors else "", date=date if not "date is required" in errors else "", errors=errors)

    # Create the XML document
    root = ET.Element("tei")
    ET.SubElement(root, "title").text = title
    ET.SubElement(root, "author").text = author
    ET.SubElement(root, "date").text = date
    tree = ET.ElementTree(root)

    xmlstr = ET.tostring(root, encoding='utf-8')
    xml_1 = xml.dom.minidom.parseString(xmlstr)
    pretty_xml_as_string = xml_1.toprettyxml()

    file_like = io.BytesIO(pretty_xml_as_string.encode('utf-8'))
    file_like.seek(0)

    return send_file(file_like,
                 mimetype='text/xml',
                 as_attachment=True,
                 attachment_filename='person.xml')


if __name__ == '__main__':
    app.run()
