import os
import re
import shutil

from os import listdir
from os.path import isfile, join

from crowdtask import create_app, db
from crowdtask.models import *
from crowdtask.dbquery import DBQuery

from flask_script import Manager, prompt_bool
from flask_migrate import Migrate, MigrateCommand


re_data = re.compile(r'(.*?): (.*?)\n')

app = create_app()
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)


@manager.command
def dropdb():
    '''Drops all database tables.'''
    if prompt_bool('Are you sure to drop your databse?'):
        db.drop_all()

@manager.option('-d', '--dir', dest='directory', default='data')
@manager.option('-n', '--filename', dest='filename', default=None)
def import_articles(directory, filename):
    '''Insert Articles to database.'''
    print "import articles from %s" % directory
    all_files = [file for file in listdir(directory) if isfile(join(directory, file))]

    for file in all_files:
        if file == ".DS_Store":
            continue
        print "Read Article: %s/%s ..." % (directory, file)
        r = open("%s/%s" % (directory, file), "r")
        content = r.read().decode('utf-8')
        all_match = re_data.findall(content)
        data = dict(all_match)

        article_title = data['Title'].strip()
        article_authors = data['Authors'].strip()
        article_source = data['Source'].strip()
        article_year = data['Year'].strip()
        article_content = data['Introduction'].strip()
        article_paragraphs = article_content.split('<BR>')

        #check whether article is exist
        article = DBQuery().get_article_by_title_and_authors(article_title, article_authors)
        if article:
            print "file exist!"
            if not isfile(join('data-in-db',file)):
                shutil.move('%s/%s' % (directory, file), 'data-in-db')
            continue

        print "insert article to the database ..."
        list = [i.strip() for i in article_paragraphs if i]
        clear_content = "<BR>".join(list)

        article_id = DBQuery().add_article(article_title, clear_content, article_authors, article_source, int(article_year))


        #for idx, paragraph in enumerate(article_paragraphs):
        #    paragraph = paragraph.strip()
        #    paragraph_id = DBQuery().add_paragraph(article_id, idx, paragraph)
        #    print "insert article %s - paragraph %s to the database ..." % (article_title, idx)


        print "move article to data-in-db folder ..."
        if isfile(join('data-in-db',file)):
            print "file has already existed in data-in-db folder..."
        else:
            shutil.move('%s/%s' % (directory, file), 'data-in-db')

if __name__ == '__main__':
    manager.run()
