from app import db
from app.models import User, Subscription, SubscriptionAction, SubscriptionLog, SubscriptionType, Client, \
     ClientToSubscription, Application, ApplicationToClient, Discount
from wtforms.widgets import TextInput, HTMLString
from wtforms import StringField

def join_clients_and_subscriptions(include_archived=False):
    """
        Returns query with joined entries Client-Subscription-ClientToSubscription
    """
    query = db.session.query(Client, Subscription, ClientToSubscription)
    query = query.join(ClientToSubscription.owner)
    query = query.join(ClientToSubscription.subscription)
    if not include_archived:
        query = query.filter(Subscription.is_archived == False)
    return query

def build_entries_to_display_subscriptions(joined_query):
    """
        Returns dictionary of labels (keys) and subscription entries, which includes
        additionally to subscription data owner's full name and so on;
        expects a query with Client and Subscription entries joined (in that order) or
        False (in that case it will return empty dictionary with labels only)
    """
    subscriptions_to_display = {
        'Номер абонемента': [],
        'ФИО': [],
        'Штрих-код': [],
        'Тип абонемента': [],
        'Скидка': [],
        'Цена': [],
        'Долг': [],
        'Количество посещений': [],
        'Создано': [],
        'Действует до': [],
        'В архиве?': [],
        'Заморожен?': [],
        'Использована заморозка без уважительной причины?': [],
        'Причина текущей заморозки': [],
        'Комментарий': [],
    }
    if joined_query:
        entries = joined_query.all()
        for entry in entries:
            subscriptions_to_display['Номер абонемента'].append(entry.Subscription.subscription_id)
            subscriptions_to_display['ФИО'].append(entry.Client.full_name)
            subscriptions_to_display['Штрих-код'].append(entry.Client.barcode)
            subscriptions_to_display['Тип абонемента'].append(entry.Subscription.subscription_type.name)
            subscriptions_to_display['Скидка'].append(entry.Subscription.discount_type.name)
            subscriptions_to_display['Цена'].append(entry.Subscription.price)
            subscriptions_to_display['Долг'].append(entry.Subscription.debt)
            subscriptions_to_display['Количество посещений'].append(entry.Subscription.visit_number)
            subscriptions_to_display['Создано'].append(entry.Subscription.created)
            subscriptions_to_display['Действует до'].append(entry.Subscription.active_up_to)
            subscriptions_to_display['В архиве?'].append(entry.Subscription.is_archived)
            subscriptions_to_display['Заморожен?'].append(entry.Subscription.is_frozen)
            subscriptions_to_display['Использована заморозка без уважительной причины?'].append(entry.Subscription.is_non_sick_freeze_used)
            subscriptions_to_display['Причина текущей заморозки'].append(entry.Subscription.freeze_reason)
            subscriptions_to_display['Комментарий'].append(entry.Subscription.comment)
    return subscriptions_to_display

def get_subscription_log_to_display(query):
    """
        Returns dictionary to render it in a template that contains subscription log for each
        subscription in the query; query is a joined Client-Subscription-ClientToSubscription
        query; with False provided instead of query, returns empty dictionary
    """
    log_to_display = {
        'Номер абонемента': [],
        'Действие': [],
        'Детали': [],
        'Когда': [],
    }
    if query:
        entries = query.all()
        for entry in entries:
            subscription_id = entry.Subscription.subscription_id
            log_entries = entry.Subscription.actions_performed.order_by(SubscriptionLog.created.desc()).all()
            for log_entry in log_entries:
                log_to_display['Номер абонемента'].append(subscription_id)
                log_to_display['Действие'].append(log_entry.action.name)
                log_to_display['Детали'].append(log_entry.details)
                log_to_display['Когда'].append(log_entry.created)
    return log_to_display

def disconnect_client_from_his_applications(client):
    """
        Takes Client entry and deletes any corresponding ApplicationToClient and Application entries
        if there is no other Client entries connected to them
    """
    applications_to_client = client.applications.all()
    is_there_is_another_client_connected = [False]*len(applications_to_client)
    for index, application_to_client in enumerate(applications_to_client):
        if len(ApplicationToClient.query.filter_by(application_id=application_to_client.application_id).all()) > 1:
            is_there_is_another_client_connected[index] = True
    applications_to_client = [a_to_c for (a_to_c, criteria) in zip(applications_to_client,
                              is_there_is_another_client_connected) if not criteria]
    applications = [application_to_client.image for application_to_client in applications_to_client]
    for application in applications:
        db.session.delete(application)
    for application_to_client in applications_to_client:
        db.session.delete(application_to_client)
    db.session.commit()


class DatalistInput(TextInput):
    """
    Custom widget to create an input with a datalist attribute
    """

    def __init__(self, datalist=""):
        super(DatalistInput, self).__init__()
        self.datalist = datalist

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('name', field.name)

        # field.default - default value which you set in route as form.field.default = ... (at the begin is None)
        # field._value() - value which you get from the form on submit and can use.

        if field.default is None:
            value = ""
        else:
            value = field.default

        html = [u'<input list="{}_list" id="{}", name="{}" value="{}">'.
                    format(field.id, field.id, field.name, value),
                u'<datalist id="{}_list">'.format(field.id)]

        for item in field.datalist:
            html.append(u'<option value="{}">'.format(item))
        html.append(u'</datalist>')

        return HTMLString(u''.join(html))


class DatalistField(StringField):
    """
    Custom field type for datalist input
    """
    widget = DatalistInput()

    def __init__(self, label=None, datalist="", validators=None, **kwargs):
        super(DatalistField, self).__init__(label, validators, **kwargs)
        self.datalist = datalist

    def _value(self):
        if self.data:
            return u''.join(self.data)
        else:
            return u''


