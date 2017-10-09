#!/usr/bin/env python3

import click
from flask import Flask
from elasticsearch import Elasticsearch
from elasticsearch.client import IndicesClient, CatClient

es = Elasticsearch()
index = IndicesClient(es)
cat = CatClient(es)

annif = Flask(__name__)

annif.config.from_object('annif.config.Config')


projectIndexConf = {
        'mappings': {
            'project': {
                'properties': {
                    'name': {
                        'type': 'text'
                        },
                    'language': {
                        'type': 'text'
                        },
                    'analyzer': {
                        'type': 'text'
                        }
                    }
                }
            }
        }


@annif.cli.command('init')
def init():
    """
    Generate the Elasticsearch repository for projects.

    Usage: annif init
    """
    if index.exists(annif.config['INDEX_NAME']):
        index.delete(annif.config['INDEX_NAME'])
    return es.indices.create(index=annif.config['INDEX_NAME'],
                             body=projectIndexConf)


@annif.cli.command('list-projects')
def listprojects():
    """
    List available projects.

    Usage: annif list-projects

    REST equivalent: GET /projects/
    """

    doc = {
            'size': 1000,
            'query': {
                'match_all': {}
                }
            }
    results = es.search(index=annif.config['INDEX_NAME'], doc_type='project',
            body=doc)
    projects = [x['_source'] for x in results['hits']['hits']]
    for p in projects:
        print(p)

    print(projects)
    report = cat.indices()  # This queries different indices and returns
    # a report string, if it's needed

    return projects


@annif.cli.command('show-project')
@click.argument('projectid')
def showProject(projectid):
    """
    Show project information.

    Usage: annif show-project <projectId>

    REST equivalent:

    GET /projects/<projectId>
    """
    pass



def parseIndexname(projectid):
    return "{0}-{1}".format(annif.config['INDEX_NAME'], projectid)


@annif.cli.command('create-project')
@click.argument('projectid')
@click.option('--language')
@click.option('--analyzer')
def createProject(projectid, language, analyzer):
    """
    Create a new project.

    Usage: annif create-project <projectId> --language <lang> --analyzer
    <analyzer>

    REST equivalent:

    PUT /projects/<projectId>
    """
    proj_indexname = parseIndexname(projectid)

    # Create an index for the project
    index.create(index=proj_indexname)

    # Add the details of the new project to the 'master' index
    resp = es.create(index=annif.config['INDEX_NAME'], doc_type='project',
                     id=projectid,
                     body={'name': projectid, 'language': language,
                           'analyzer': analyzer})
    print(resp)


@annif.cli.command('drop-project')
@click.argument('projectid')
def dropProject(projectid):
    """
    Delete a project.
    USAGE: annif drop-project <projectid>

    REST equivalent:

    DELETE /projects/<projectid>
    """
    # Delete the index from the 'master' index
    result = es.delete(index=annif.config['INDEX_NAME'],
            doc_type='project', id=projectid)

    print(result)

    # Then delete the project index
    result = index.delete(index=parseIndexname(projectid))
    print(result)


@annif.cli.command('list-subjects')
@click.argument('projectid')
def listSubjects(projectid):
    """
    Show all subjects for a project.

    USAGE: annif list-subjects <projectid>

    REST equivalent:

    GET /projects/<projectid>/subjects
    """
    pass


@annif.cli.command('show-subject')
@click.argument('projectid')
@click.argument('subjectid')
def showSubject(projectid, subjectid):
    """
    Show information about a subject.

    USAGE: annif show-subject <projectid> <subjectid>

    REST equivalent:

    GET /projects/<projectid>/subjects/<subjectid>
    """
    pass


@annif.cli.command('create-subject')
@click.argument('projectid')
@click.argument('subjectid')
def createSubject(projectid, subjectid):
    """
    Create a new subject, or update an existing one.

    annif create-subject <projectid> <subjectid> <subject.txt

    REST equivalent:

    PUT /projects/<projectid>/subjects/<subjectid>
    """
    pass


@annif.cli.command('load')
@click.argument('projectid')
@click.argument('directory')
@click.option('--clear', default=False)
def load(projectid, directory, clear):
    """
    Load all subjects from a directory.

    USAGE: annif load <projectid> <directory> [--clear=CLEAR]
    """
    pass


@annif.cli.command('drop-subject')
@click.argument('projectid')
@click.argument('subjectid')
def dropSubject(projectid, subjectid):
    """
    Delete a subject.

    USAGE: annif drop-subject <projectid> <subjectid>

    REST equivalent:

    DELETE /projects/<projectid>/subjects/<subjectid>

    """
    pass


@annif.cli.command('analyze')
@click.option('--maxhits', default=20)
@click.option('--threshold', default=0.9)  # TODO: Check this.
def analyze(projectid, maxhits, threshold):
    """"
    Delete a subject.

    USAGE: annif drop-subject <projectid> <subjectid>

    REST equivalent:

    DELETE /projects/<projectid>/subjects/<subjectid>

    """
    pass


@annif.route('/')
def start():
    return 'Started application'


if __name__ == "__main__":
    annif.run(port=8000)
