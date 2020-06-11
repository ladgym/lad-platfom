from datetime import datetime
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask_login._compat import PY2, text_type
from datetime import datetime, timedelta

class BaseModel():
    created = db.Column(db.DateTime, default=datetime.utcnow)
    updated = db.Column(db.DateTime, default=datetime.utcnow)


class UserRoles(BaseModel, db.Model):
    # roles include:
    # ones who are able to edit everything
    # ones who are restricted to edit only subscriptions groups and so on
    # ones who are allowed only to see schedule and other training personnel info
    # ones who are allowed only to view their own subscriptions
    role_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return "<Role {}>".fornmat(self.name)

class User(BaseModel, db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('user_roles.role_id'))
    deactivated = db.Column(db.DateTime)
    subscriptions = db.relationship('Subscription', backref='creator', lazy='dynamic')
    subscription_log = db.relationship('SubscriptionLog', backref='actor', lazy='dynamic')

    @property
    def is_deactivated(self):
        return bool(self.deactivated)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def is_active(self):
        return True

    def get_id(self):
        try:
            return text_type(self.user_id)
        except AttributeError:
            raise NotImplementedError('No `id` attribute - override `get_id`')

    def set_password(self, password):
        self.password = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def __repr__(self):
        return '<User {}>'.format(self.email)

@login.user_loader
def load_user(id):
    return User.query.filter_by(user_id=int(id)).first()

class Subscription(BaseModel, db.Model):
    subscription_id = db.Column(db.Integer, primary_key=True)
    subscription_type_id = db.Column(db.Integer, db.ForeignKey('subscription_type.subscription_type_id'))
    discount_id = db.Column(db.Integer, db.ForeignKey('discount.discount_id'))
    created_by = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    price = db.Column(db.Float(8))
    debt = db.Column(db.Float(8))
    visit_number = db.Column(db.Integer, index=True)
    active_up_to = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    is_frozen = db.Column(db.Boolean, default=False)
    is_non_sick_freeze_used = db.Column(db.Boolean, default=False)
    freeze_reason = db.Column(db.Text(250))
    is_archived = db.Column(db.Boolean, default=False)
    comment = db.Column(db.Text(500))
    actions_performed = db.relationship('SubscriptionLog', backref='operand', lazy='dynamic')
    client = db.relationship('ClientToSubscription', backref='subscription', lazy='dynamic')

    def __repr__(self):
        return '<Subscription {}>'.format(self.subscription_id)

    def perform_template_action_by_id(self, action_id, current_user):
        action = SubscriptionAction.query.get(action_id)
        if action is None:
            return False
        if 'visits_change' in action.details_template:
            self.visit_number += action.details_template['visits_change']
        if 'active_up_to_change' in action.details_template:
            self.active_up_to += timedelta(days=action.details_template['active_up_to_change'])
        if 'freeze' in action.details_template:
            self.is_frozen = action.details_template['freeze']
        if 'use_non_sick_freeze' in action.details_template:
            self.is_non_sick_freeze_used = True
        entry = SubscriptionLog(subscription_id=self.subscription_id,
                                subscription_action_id=action.subscription_action_id, created_by=current_user.user_id,
                                details=action.details_template)
        db.session.add(entry)
        db.session.commit()
        return u'Над абонементом {} произведено действие {}'.format(self.subscription_id, action.name)

    def perform_action_by_id(self, action_id, current_user, additional_parameter=None):
        #: to do: take additional parameter into account
        action = SubscriptionAction.query.get(action_id)
        if action is None:
            return False
        if 'visits_change' in action.details_template:
            self.visit_number += action.details_template['visits_change']
        if 'active_up_to_change' in action.details_template:
            self.active_up_to += timedelta(days=action.details_template['active_up_to_change'])
        if 'freeze' in action.details_template:
            self.is_frozen = action.details_template['freeze']
        if 'use_non_sick_freeze' in action.details_template:
            self.is_non_sick_freeze_used = True
        entry = SubscriptionLog(subscription_id=self.subscription_id,
                                subscription_action_id=action.subscription_action_id, created_by=current_user.user_id,
                                details=action.details_template)
        db.session.add(entry)
        db.session.commit()
        return u'Над абонементом {} произведено действие {}'.format(self.subscription_id, action.name)

class SubscriptionType(BaseModel, db.Model):
    subscription_type_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    price = db.Column(db.Float(8))
    visit_number = db.Column(db.Integer)
    # number of months, float because it can be 6 weeks for example
    # in such case month will be accounted as 28 days
    active_period = db.Column(db.Float)
    # number in weeks
    freeze_period = db.Column(db.Integer)
    is_archived = db.Column(db.Boolean, default=False)
    subscriptions = db.relationship('Subscription', backref='subscription_type', lazy='dynamic')

    def __repr__(self):
        return '<Subscription type {}>'.format(self.name)

class Discount(BaseModel, db.Model):
    discount_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text(250))
    value = db.Column(db.Integer)
    is_archived = db.Column(db.Boolean, default=False)
    subscriptions = db.relationship('Subscription', backref='discount_type', lazy='dynamic')

    def __repr__(self):
        return '<Discount {}>'.format(self.name)

class SubscriptionLog(BaseModel, db.Model):
    subscription_log_id = db.Column(db.Integer, primary_key=True)
    subscription_id = db.Column(db.Integer, db.ForeignKey('subscription.subscription_id'), index=True)
    subscription_action_id = db.Column(db.Integer, db.ForeignKey('subscription_action.subscription_action_id'), index=True)
    details = db.Column(db.JSON)
    created_by = db.Column(db.Integer, db.ForeignKey('user.user_id'))

    def __repr__(self):
        return '<SubscriptionLog {} {}>'.format(self.subscription_log_id, self.details)

class SubscriptionAction(BaseModel, db.Model):
    subscription_action_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    details_template = db.Column(db.JSON)
    all_such_actions = db.relationship('SubscriptionLog', backref='action', lazy='dynamic')

    def __repr__(self):
        return '<SubscriptionAction {}>'.format(self.name)

class Client(BaseModel, db.Model):
    client_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), index=True)
    last_name = db.Column(db.String(100), index=True)
    middle_name = db.Column(db.String(100), index=True)
    full_name = db.Column(db.String(150), index=True)
    birthday = db.Column(db.DateTime)
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    additional_info = db.Column(db.Text(500))
    allow_email_notifications = db.Column(db.Boolean, default=False)
    allow_phone_notifications = db.Column(db.Boolean, default=False)
    barcode = db.Column(db.Integer, index=True)
    comment = db.Column(db.Text(500))
    in_relations_with = db.Column(db.String)
    subscriptions = db.relationship('ClientToSubscription', backref='owner', lazy='dynamic')
    applications = db.relationship('ApplicationToClient', backref='owner', lazy='dynamic')


    def __repr__(self):
        return '<Client {} {}>'.format(self.first_name, self.last_name)

class ClientToSubscription(BaseModel, db.Model):
    client_id = db.Column(db.Integer, db.ForeignKey('client.client_id'), primary_key=True)
    subscription_id = db.Column(db.Integer, db.ForeignKey('subscription.subscription_id'), primary_key=True)

    def __repr__(self):
        return '<ClientToSubscription client id: {}, subscription id: {}>'.format(self.client_id, self.subscription_id)

class ApplicationToClient(BaseModel, db.Model):
    client_id = db.Column(db.Integer, db.ForeignKey('client.client_id'), primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('application.application_id'))


    def __repr__(self):
        return '<ApplicationToClient client id: {}, application id: {}>'.format(self.client_id, self.application_id)

class Application(BaseModel, db.Model):
    application_id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.LargeBinary)
    whose = db.relationship('ApplicationToClient', backref='image', lazy='dynamic')

    def __repr__(self):
        return '<Application image of application id: {}>'.format(self.application_id)