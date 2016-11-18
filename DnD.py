import os
from _curses import flash
#
from flask import Flask, redirect, render_template, session, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from wtforms import Form, StringField
from wtforms.validators import Required

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
db = SQLAlchemy(app)


bootstrap = Bootstrap(app)


# Forms
class LoginForm(Form):
    username = StringField("Username", validators=[Required()])
    # Make passwords hidden later
    password = StringField("Password", validators=[Required()])
    def __repr__(self):
        return self.username


# Database classes
class User(db.Model):
    __tablename__ = "User"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(64))
    campaigns = db.relationship('Campaign', secondary='user_campaign_link')


# connection for User-to-Campaign many-to-many relationship
class UserCampaignLink(db.Model):
    __tablename__ = "user_campaign_link"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'))
    campaign_id = db.Column(db.Integer, db.ForeignKey('Campaign.id'))
    is_DM = db.Column(db.Boolean)
    user = db.relationship('User', backref=db.backref('campaign_assoc'))
    campaign = db.relationship('Campaign', backref=db.backref('user_assoc'))


class Campaign(db.Model):
    __tablename__ = "Campaign"
    id = db.Column(db.Integer, primary_key=True)
    events = db.relationship('Event', backref='campaign')
    users = db.relationship('User', secondary='user_campaign_link')


class Event(db.Model):
    __tablename__ = "EventLog"
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('Campaign.id'))
    summary = db.Column(db.String(256))
    description = db.Column(db.String(256))


class Character(db.Model):
    __tablename__ = "Character"
    # IDs
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'))
    campaign_id = db.Column(db.Integer, db.ForeignKey('Campaign.id'))
    # basic character info
    name = db.Column(db.String(64))
    race = db.Column(db.String(64))
    cClass = db.Column(db.String(64))
    level = db.Column(db.Integer)
    hit_dice = db.Column(db.String())
    total_hit_dice = db.Column(db.Integer)
    prof_bonus = db.Column(db.Integer)
    exp_points = db.Column(db.Integer)
    armor_class = db.Column(db.Integer)
    speed = db.Column(db.Integer)
    max_HP = db.Column(db.Integer)
    curr_HP = db.Column(db.Integer)
    temp_HP = db.Column(db.Integer)
    # abilities
    str = db.Column(db.Integer)
    dex = db.Column(db.Integer)
    con = db.Column(db.Integer)
    int = db.Column(db.Integer)
    wis = db.Column(db.Integer)
    cha = db.Column(db.Integer)
    # ability modifiers
    str_mod = db.Column(db.Integer)
    dex_mod = db.Column(db.Integer)
    con_mod = db.Column(db.Integer)
    int_mod = db.Column(db.Integer)
    wis_mod = db.Column(db.Integer)
    cha_mod = db.Column(db.Integer)
    # saving throws
    str_save = db.Column(db.Boolean)
    dex_save = db.Column(db.Boolean)
    con_save = db.Column(db.Boolean)
    int_save = db.Column(db.Boolean)
    wis_save = db.Column(db.Boolean)
    cha_save = db.Column(db.Boolean)
    # skills
    acrobatics = db.Column(db.Boolean)
    animal_handling = db.Column(db.Boolean)
    arcana = db.Column(db.Boolean)
    athletics = db.Column(db.Boolean)
    deception = db.Column(db.Boolean)
    history = db.Column(db.Boolean)
    insight = db.Column(db.Boolean)
    intimidation = db.Column(db.Boolean)
    investigation = db.Column(db.Boolean)
    medicine = db.Column(db.Boolean)
    nature = db.Column(db.Boolean)
    perception = db.Column(db.Boolean)
    performance = db.Column(db.Boolean)
    persuasion = db.Column(db.Boolean)
    religion = db.Column(db.Boolean)
    sleight_of_hand = db.Column(db.Boolean)
    stealth = db.Column(db.Boolean)
    survival = db.Column(db.Boolean)


@app.route('/login', methods=["POST"])
def login():
    if (session['username'] == None):
        username = None
        password = None
        form = LoginForm()
        if (form.validate_on_submit()):
            for user in User.query.all():
                if (user.username == form.username.data and user.password == form.password.data):
                    flash('You are now logged in as ' + user.username)
                    session['username'] = user.username
                    form.username.data = ''
                    form.password.data = ''
                    return redirect(url_for('home'))
            flash('There is no user with that password')
            form.username.data = ''
            form.password.data = ''
            return redirect(url_for('login'))
        return render_template("login.html", form=form, name=username)
    return render_template("loggedIn.html", name=session['username'])


@app.route('/new_user', methods=["POST"])
def newUser():
    if (session['username'] == None):
        username = None
        password = None
        form = LoginForm()
        if (form.validate_on_submit()):
            if (form.username.data in [user.username for user in User.query.all()]):
                flash(form.username.data + ' is already in the database')
                form.username.data = ''
                form.password.data = ''
                return redirect(url_for('new_user'))
            flash('Your account, ' + form.name.data + ', has been created')
            username = form.username.data
            password = form.password.data
            user = User(username=username, password=password)
            db.session.add(user)
            form.username.data = ''
            form.password.data = ''
            return redirect(url_for('new_game'))
        return render_template("newUser.html", form=form, name=username)
    return render_template("loggedIn.html", name=session['username'])


def testUser():
    db.session.add(User(username='erumbold', password='0923'))
    db.session.add(User(username='bbenson', password='1234'))
    db.session.commit()


def testCampaign():
     db.session.add(Campaign())
     db.session.add(UserCampaignLink(user_id=1, campaign_id=1, is_DM=True))
     db.session.add(UserCampaignLink(user_id=2, campaign_id=1, is_DM=False))
     db.session.commit()

def testCharacter():
    name = 'Largren Grathson'
    race = 'Hill Dwarf'
    cClass = 'Fighter'
    level = 8
    hit_dice = 'd10'
    total_hit_dice = 8
    prof_bonus = 3
    exp_points = 0
    armor_class = 16
    speed = 30
    max_HP = 85
    curr_HP = 85
    temp_HP = 0
    str = 10
    dex = 14
    con = 14
    int = 10
    wis = 13
    cha = 13
    str_mod = 1
    dex_mod = 4
    con_mod = 2
    int_mod = 0
    wis_mod = 0
    cha_mod = 1
    str_save = False
    dex_save = True
    con_save = True
    int_save = False
    wis_save = False
    cha_save = False
    acrobatics = True
    animal_handling = False
    arcana = False
    athletics = True
    deception = True
    history = False
    insight = False
    intimidation = False
    investigation = False
    medicine = False
    nature = False
    perception = True
    performance = False
    persuasion = False
    religion = False
    sleight_of_hand = False
    stealth = False
    survival = False
    db.session.add(Character(user_id=2, campaign_id=1, name=name, race=race, cClass=cClass, level=level, hit_dice=hit_dice, total_hit_dice=total_hit_dice,
                   prof_bonus=prof_bonus, exp_points=exp_points, armor_class=armor_class, speed=speed, max_HP=max_HP,
                   curr_HP=curr_HP, temp_HP=temp_HP, str=str, dex=dex, con=con, int=int, wis=wis, cha=cha, str_mod=str_mod,
                   dex_mod=dex_mod, con_mod=con_mod, int_mod=int_mod, wis_mod=wis_mod, cha_mod=cha_mod, str_save=str_save,
                   dex_save=dex_save, con_save=con_save, int_save=int_save, wis_save=wis_save, cha_save=cha_save,
                   acrobatics=acrobatics, animal_handling=animal_handling, arcana=arcana, athletics=athletics, deception=deception,
                   history=history, insight=insight, intimidation=intimidation, investigation=investigation, medicine=medicine,
                   nature=nature, perception=perception, performance=performance, persuasion=persuasion, religion=religion,
                   sleight_of_hand=sleight_of_hand, stealth=stealth, survival=survival))
    db.session.commit()


def testEvent():
    summary = "A long time ago in a galaxy far, far away"
    description = "It is a period of civil war. Rebel spaceships, striking from a hidden base, have won their first victory against the evil Galactic Empire."
    db.session.add(Event(campaign_id=1, summary=summary, description=description))
    db.session.commit()

if __name__ == '__main__':
    db.drop_all()
    db.create_all()
    testUser()
    testCampaign()
    testCharacter()
    testEvent()
    db.session.commit()
    app.run()
