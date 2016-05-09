from flask import Blueprint, Flask, render_template


views = Blueprint('views', __name__, template_folder='templates')


@views.route('/')
def index():
    return render_template('index.html')

@views.route('/topic')
def topic_task():
    data = {
        'title': "Criosity Killed the Cat, but Makes Crowdwork Better",
        'content': "Crowdsourcing systems organize individuals to solve complex problems that are otherwise difficult to solve computationally [cited]. A key challenge in creating these systems is to sufficiently incentivize individuals to participate and keep producing high quality work. In support of this goal, a wide range of incentive mechanisms have been designed and studied in crowdsourcing and social computing settings, including monetary payment [cited], gamification techniques [cited], social comparisons [cited], visualizations and facilitation [cited], and virtual reward systems [cited]. The efficacy of these approaches ranges quite a bit, making this an active, open research area."
    }
    print data['content']
    return render_template('topic_task.html', data=data)

@views.route('/relevance')
def relevance_task():
    data = {
        'title': "Criosity Killed the Cat, but Makes Crowdwork Better",
        'content': "Crowdsourcing systems organize individuals to solve complex problems that are otherwise difficult to solve computationally [cited]. A key challenge in creating these systems is to sufficiently incentivize individuals to participate and keep producing high quality work. In support of this goal, a wide range of incentive mechanisms have been designed and studied in crowdsourcing and social computing settings, including monetary payment [cited], gamification techniques [cited], social comparisons [cited], visualizations and facilitation [cited], and virtual reward systems [cited]. The efficacy of these approaches ranges quite a bit, making this an active, open research area.",
        'topic_sentence': [0, 3]
    }
    return render_template('relevance_task.html', data=data)

@views.route('/relation')
def relation_task():
    content = "Crowdsourcing systems organize individuals to solve complex problems that are otherwise difficult to solve computationally [cited]. A key challenge in creating these systems is to sufficiently incentivize individuals to participate and keep producing high quality work. In support of this goal, a wide range of incentive mechanisms have been designed and studied in crowdsourcing and social computing settings, including monetary payment [cited], gamification techniques [cited], social comparisons [cited], visualizations and facilitation [cited], and virtual reward systems [cited]. The efficacy of these approaches ranges quite a bit, making this an active, open research area."
    content_list = content.split(".")

    data = {
        'title': "Criosity Killed the Cat, but Makes Crowdwork Better",
        'content_list': content_list,
        'pair_ids': [1,2],
    }
    return render_template('relation_task.html', data=data)
