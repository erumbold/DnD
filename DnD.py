import os
from flask import Flask, redirect, render_template, session, url_for, flash
from flask.ext.sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf import Form
from wtforms import StringField, SubmitField, PasswordField, IntegerField, BooleanField, SelectField
from wtforms.validators import Required


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
db = SQLAlchemy(app)


bootstrap = Bootstrap(app)


# TODO:
# 1.Logging in (COMPLETE)
# 2.Logging out (COMPLETE)
# 3.Viewing a Character (COMPLETE)
# 4.Creating a Character (COMPLETE)
# 5.Adding Characters to Campaigns (COMPLETE)
# 6.Being able to make people DMs of a campaign
# 7.Adding logs to a campaign
# 8.Sending an email to everyone in a campaign at once and individually (DM feature)


# Forms
class LoginForm(Form):
    username = StringField("Username", validators=[Required()])
    password = PasswordField("Password", validators=[Required()])
    submit = SubmitField("Continue")


class AddCharForm(Form):
    character = SelectField(label="Character", coerce=int, validators=[Required()])
    submit = SubmitField("Add")


class CampaignForm(Form):
    name=StringField("Campaign Name", validators=[Required()])
    submit = SubmitField("Create")

# Must manually set Campaign, Account, curr/temp HP
class CharForm(Form):
    # basic character info
    name = StringField("Name", validators=[Required()])
    race = SelectField("Race", validators=[Required()], choices=[
        ("Human", "Human"), ("Half-Elf", "Half-Elf"), ("Elf", "Elf"),
        ("Dwarf", "Dwarf"), ("Gnome", "Gnome"), ("Halfling", "Halfling"),
        ("Half-Orc", "Half-Orc")
    ])
    level = IntegerField("Level", validators=[Required()])
    cClass = SelectField("Class", validators=[Required()], choices=[
        ("Fighter", "Fighter"), ("Sorcerer", "Sorcerer"), ("Wizard", "Wizard"),
        ("Ranger", "Ranger"), ("Rogue", "Rogue"), ("Paladin", "Paladin"),
        ("Bard", "Bard"), ("Barbarian", "Barbarian"), ("Cleric", "Cleric"),
        ("Monk", "Monk")
    ])
    hit_dice = SelectField("Hit Dice", validators=[Required()], choices=[
        ("d12", "d12"), ("d10", "d10"), ("d8", "d8"), ("d6", "d6"), ("d4", "d4")
    ])
    total_hit_dice = IntegerField("Total Hit Dice")
    prof_bonus = IntegerField("Proficiency Bonus")
    exp_points = IntegerField("Experience Points")
    armor_class = IntegerField("Armor Class")
    speed = IntegerField("Speed")
    max_HP = IntegerField("Max HP")

    # abilities
    str = IntegerField("Strength", validators=[Required()])
    dex = IntegerField("Dexterity", validators=[Required()])
    con = IntegerField("Constitution", validators=[Required()])
    int = IntegerField("Intelligence", validators=[Required()])
    wis = IntegerField("Wisdom", validators=[Required()])
    cha = IntegerField("Charisma", validators=[Required()])

    # ability modifiers
    str_mod = IntegerField("Strength Modifier")
    dex_mod = IntegerField("Dexterity Modifier")
    con_mod = IntegerField("Constitution Modifier")
    int_mod = IntegerField("Intelligence Modifier")
    wis_mod = IntegerField("Wisdom Modifier")
    cha_mod = IntegerField("Charisma Modifier")

    # saving throws - check boxes, only pick 2
    str_save = BooleanField("Strength Save")
    dex_save = BooleanField("Dexterity Save")
    con_save = BooleanField("Constitution Save")
    int_save = BooleanField("Intelligence Save")
    wis_save = BooleanField("Wisdom Save")
    cha_save = BooleanField("Charisma Save")
    # skills - check boxes
    acrobatics = BooleanField("Acrobatics")
    animal_handling = BooleanField("Animal Handling")
    arcana = BooleanField("Arcana")
    athletics = BooleanField("Athletics")
    deception = BooleanField("Deception")
    history = BooleanField("History")
    insight = BooleanField("Insight")
    intimidation = BooleanField("Intimidation")
    investigation = BooleanField("Investigation")
    medicine = BooleanField("Medicine")
    nature = BooleanField("Nature")
    perception = BooleanField("Perception")
    performance = BooleanField("Performance")
    persuasion = BooleanField("Persuasion")
    religion = BooleanField("Religion")
    sleight_of_hand = BooleanField("Sleight of Hand")
    stealth = BooleanField("Stealth")
    survival = BooleanField("Survival")

    submit = SubmitField("Create Character")


# Database classes
class User(db.Model):
    __tablename__ = "User"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(64))
    campaigns = db.relationship('Campaign', secondary='User_Campaign_Link')


# connection for User-to-Campaign many-to-many relationship
class UserCampaignLink(db.Model):
    __tablename__ = "User_Campaign_Link"
    id = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer, db.ForeignKey('User.id'), primary_key=True)
    campaignID = db.Column(db.Integer, db.ForeignKey('Campaign.id'), primary_key=True)
    isDM = db.Column(db.Boolean)
    user = db.relationship('User', backref=db.backref('Campaign_assoc'))
    campaign = db.relationship('Campaign', backref=db.backref('User_assoc'))


class EventLog(db.Model):
    __tablename__ = "EventLog"
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('Campaign.id'))
    summary = db.Column(db.String(256))
    description = db.Column(db.String(256))


class Campaign(db.Model):
    __tablename__ = "Campaign"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    events = db.relationship('EventLog', backref='Campaign')
    users = db.relationship('User', secondary='User_Campaign_Link')


class Character(db.Model):
    __tablename__ = "Character"
    # IDs
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'))
    campaign_id = db.Column(db.Integer, db.ForeignKey('Campaign.id'))
    # basic character info
    name = db.Column(db.String(64))
    race = db.Column(db.String(64))     # drop down
    cClass = db.Column(db.String(64))   # drop down
    level = db.Column(db.Integer)
    hit_dice = db.Column(db.String())   # drop down
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

    # saving throws - check boxes, only pick 2
    str_save = db.Column(db.Boolean)
    dex_save = db.Column(db.Boolean)
    con_save = db.Column(db.Boolean)
    int_save = db.Column(db.Boolean)
    wis_save = db.Column(db.Boolean)
    cha_save = db.Column(db.Boolean)

    # skills - check boxes
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


@app.before_request
def init_session():
    if ('username' not in session.keys()):
        session['username'] = None


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# 500 Page
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route("/characters/<name>")
def character(name):
    for c in Character.query.all():
        if (c.name == name):
            campaign = Campaign.query.filter_by(id=c.campaign_id).first()
            if (campaign is not None):
                campaign_name = campaign.name
            else:
                campaign_name = None
            return render_template("Character_Sheet.html", name=c.name,
                                   campaign=campaign_name, race=c.race,
                                   cClass=c.cClass, level=c.level, hit_dice=c.hit_dice, total_hit_dice=c.total_hit_dice,
                                   prof_bonus=c.prof_bonus, exp_points=c.exp_points, armor_class=c.armor_class,
                                   speed=c.speed, max_HP=c.max_HP, curr_HP=c.curr_HP, temp_HP=c.temp_HP, str=c.str,
                                   dex=c.dex, con=c.con, int=c.int, wis=c.wis, cha=c.cha, str_mod=c.str_mod,
                                   dex_mod=c.dex_mod, con_mod=c.con_mod, int_mod=c.int_mod, wis_mod=c.wis_mod,
                                   cha_mod=c.cha_mod, str_save=c.str_save, dex_save=c.dex_save, con_save=c.con_save,
                                   int_save=c.int_save, wis_save=c.wis_save, cha_save=c.cha_save, acrobatics=c.acrobatics,
                                   animal_handling=c.animal_handling, arcana=c.arcana, athletics=c.athletics,
                                   deception=c.deception, history=c.history, insight=c.insight, intimidation=c.intimidation,
                                   investigation=c.investigation, medicine=c.medicine, nature=c.nature, perception=c.perception,
                                   performance=c.performance, persuasion=c.persuasion, religion=c.religion,
                                   sleight_of_hand=c.sleight_of_hand, stealth=c.stealth, survival=c.survival)

    return render_template("Character_Not_Found.html")


@app.route("/user/<name>")
def user(name):
    if (name in [c.username for c in User.query.all()]):
        id = User.query.filter_by(username=name).first().id
        characters = [c.name for c in Character.query.filter_by(user_id=id)]
        return render_template('User_Page.html', name=name, characters=characters)
    return render_template('404.html')


# To be called when the player clicks the logout button
@app.route("/logout")
def logout():
    session['username'] = None
    return redirect(url_for('homepage'))


@app.route('/login', methods=["GET", "POST"])
def login():
    if (session['username'] is None):
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
                    return redirect(url_for('user', name=session['username']))
            flash('There is no user with that password')
            form.username.data = ''
            form.password.data = ''
            return redirect(url_for('login'))
        return render_template("Login.html", form=form, name=username)
    return render_template("Logged_In.html", name=session['username'])


@app.route('/new-user', methods=["GET", "POST"])
def new_user():
    if (session['username'] is None):
        username = None
        password = None
        form = LoginForm()
        if (form.validate_on_submit()):
            if (form.username.data in [user.username for user in User.query.all()]):
                flash('The username ' + form.username.data + ' is already in use')
                form.username.data = ''
                form.password.data = ''
                return redirect(url_for('new_user'))
            flash('Your account, ' + form.username.data + ', has been created')
            username = form.username.data
            password = form.password.data
            user = User(username=username, password=password)
            db.session.add(user)
            form.username.data = ''
            form.password.data = ''
            session['username'] = username
            return redirect(url_for('user', name=session['username']))
        return render_template("New_User.html", form=form)
    return render_template("Logged_In.html", name=session['username'])


@app.route('/new-character', methods=["GET", "POST"])
def new_character():
    if (session['username'] is not None):
        name = None
        race = None
        cClass = None
        level = 0
        hit_dice = None
        total_hit_dice = 0
        prof_bonus = 0
        exp_points = 0
        armor_class = 0
        speed = 0
        max_HP = 0
        curr_HP = 0
        temp_HP = 0
        str = 0
        dex = 0
        con = 0
        int = 0
        wis = 0
        cha = 0
        str_mod = 0
        dex_mod = 0
        con_mod = 0
        int_mod = 0
        wis_mod = 0
        cha_mod = 0
        str_save = False
        dex_save = False
        con_save = False
        int_save = False
        wis_save = False
        cha_save = False
        acrobatics = False
        animal_handling = False
        arcana = False
        athletics = False
        deception = False
        history = False
        insight = False
        intimidation = False
        investigation = False
        medicine = False
        nature = False
        perception = False
        performance = False
        persuasion = False
        religion = False
        sleight_of_hand = False
        stealth = False
        survival = False

        form = CharForm()
        if (form.validate_on_submit()):
            name = form.name.data
            race = form.race.data
            cClass = form.cClass.data
            level = form.level.data
            hit_dice = form.hit_dice.data
            total_hit_dice = form.total_hit_dice.data
            prof_bonus = form.prof_bonus.data
            exp_points = form.exp_points.data
            armor_class = form.armor_class.data
            speed = form.speed.data
            max_HP = form.max_HP.data
            curr_HP = form.max_HP.data
            temp_HP = form.max_HP.data
            str = form.str.data
            dex = form.dex.data
            con = form.con.data
            int = form.int.data
            wis = form.wis.data
            cha = form.cha.data
            str_mod = form.str_mod.data
            dex_mod = form.dex_mod.data
            con_mod = form.con_mod.data
            int_mod = form.int_mod.data
            wis_mod = form.wis_mod.data
            cha_mod = form.cha_mod.data
            str_save = form.str_save.data
            dex_save = form.dex_save.data
            con_save = form.con_save.data
            int_save = form.int_save.data
            wis_save = form.wis_save.data
            cha_save = form.cha_save.data
            acrobatics = form.acrobatics.data
            animal_handling = form.animal_handling.data
            arcana = form.arcana.data
            athletics = form.athletics.data
            deception = form.deception.data
            history = form.history.data
            insight = form.insight.data
            intimidation = form.intimidation.data
            investigation = form.investigation.data
            medicine = form.medicine.data
            nature = form.nature.data
            perception = form.perception.data
            performance = form.performance.data
            persuasion = form.persuasion.data
            religion = form.religion.data
            sleight_of_hand = form.sleight_of_hand.data
            stealth = form.stealth.data
            survival = form.survival.data

            userID = User.query.filter_by(username=session['username']).first().id
            campaignID = -1

            db.session.add(Character(user_id=userID, campaign_id=campaignID, name=name, race=race, cClass=cClass, level=level, hit_dice=hit_dice,
                          total_hit_dice=total_hit_dice,
                          prof_bonus=prof_bonus, exp_points=exp_points, armor_class=armor_class, speed=speed,
                          max_HP=max_HP,
                          curr_HP=curr_HP, temp_HP=temp_HP, str=str, dex=dex, con=con, int=int, wis=wis, cha=cha,
                          str_mod=str_mod,
                          dex_mod=dex_mod, con_mod=con_mod, int_mod=int_mod, wis_mod=wis_mod, cha_mod=cha_mod,
                          str_save=str_save,
                          dex_save=dex_save, con_save=con_save, int_save=int_save, wis_save=wis_save, cha_save=cha_save,
                          acrobatics=acrobatics, animal_handling=animal_handling, arcana=arcana, athletics=athletics,
                          deception=deception,
                          history=history, insight=insight, intimidation=intimidation, investigation=investigation,
                          medicine=medicine,
                          nature=nature, perception=perception, performance=performance, persuasion=persuasion,
                          religion=religion,
                          sleight_of_hand=sleight_of_hand, stealth=stealth, survival=survival))

            flash("Your character, " + name + ", has been created")
            name = None
            race = None
            cClass = None
            level = 0
            hit_dice = None
            total_hit_dice = 0
            prof_bonus = 0
            exp_points = 0
            armor_class = 0
            speed = 0
            max_HP = 0
            curr_HP = 0
            temp_HP = 0
            str = 0
            dex = 0
            con = 0
            int = 0
            wis = 0
            cha = 0
            str_mod = 0
            dex_mod = 0
            con_mod = 0
            int_mod = 0
            wis_mod = 0
            cha_mod = 0
            str_save = False
            dex_save = False
            con_save = False
            int_save = False
            wis_save = False
            cha_save = False
            acrobatics = False
            animal_handling = False
            arcana = False
            athletics = False
            deception = False
            history = False
            insight = False
            intimidation = False
            investigation = False
            medicine = False
            nature = False
            perception = False
            performance = False
            persuasion = False
            religion = False
            sleight_of_hand = False
            stealth = False
            survival = False
            return redirect(url_for('new_character'))
        return render_template("Create_Character.html", form=form)
    return render_template("Must_Login.html", name=session['username'])

@app.route('/characters')
def character_list():
    if (session['username'] is None):
        return render_template("Must_Login.html")

    id = User.query.filter_by(username=session['username']).first().id
    characters = [c.name for c in Character.query.filter_by(user_id=id)]

    return render_template('Characters.html', name=session['username'], characters=characters)


@app.route('/new-campaign', methods=['GET', 'POST'])
def new_campaign():
    if (session['username'] is not None):
        name = None
        form = CampaignForm()

        if (form.validate_on_submit()):
            flash(form.name.data + ' has been created')
            name = form.name.data
            campaign = Campaign(name=name)
            db.session.add(campaign)
            form.name.data = ''
            return redirect(url_for('new_campaign'))

        return render_template("New_Campaign.html", form=form)

    return render_template("Must_Login.html", name=session['username'])


@app.route('/campaigns/<name>')
def campaign(name):
    campaign = Campaign.query.filter_by(name=name).first()
    if (campaign is not None):
        characters = [c.name for c in Character.query.filter_by(campaign_id=campaign.id).all()]
        return render_template('Campaign.html', campaign=name, characters=characters)

    return render_template('404.html')


@app.route('/<name>/add-character', methods=['GET', 'POST'])
def add_character(name):
    if (session['username'] is not None):
        user = User.query.filter_by(username=session['username']).first()

        form = AddCharForm()
        form.character.choices = [(c.id, c.name) for c in Character.query.filter_by(user_id=user.id)]


        if (form.validate_on_submit()):
            charID = form.character.data
            character = Character.query.filter_by(id=charID).first()
            campaign = Campaign.query.filter_by(name=name).first()
            character.campaign_id = campaign.id

            # User Campaign Linking (Currently non-functional due to NOT NULL/Flush Errors)
            # updates  the user's campaigns M2M table (should be its own function later)

            # One of these two methods is supposed to work, but doesn't due to some error
            # characters = Character.query.filter_by(user_id=user.id).all()
            # user.campaigns = [Campaign.query.filter_by(id=c.campaign_id).first() for c in characters]

            # temp = UserCampaignLink(user=user, campaign=campaign, isDM=False)
            # db.session.add(temp)

            flash("Your character's active campaign has been changed")
            form.character.choices = []
            form.character.data = -1
            return redirect(url_for('campaign', name=campaign.name))

        return render_template('Add_Character_To_Campaign.html', form=form)

    return render_template('Must_Login.html')


@app.route('/campaigns')
def campaign_list():
    if (session['username'] is not None):
        campaigns = [c.name for c in Campaign.query.all()]
        return render_template("Campaigns.html", campaigns=campaigns)

    return render_template("Must_Login.html")


@app.route('/')
def homepage():
    return render_template("Home.html")


if __name__ == '__main__':
    db.create_all()
    app.run()
