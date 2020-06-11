from flask import render_template, flash
from app import db
from app.mainpage import bp
from flask_login import login_required, current_user
from app.mainpage.forms import FindSubscriptionByName, FindSubscriptionByBarcode, PerformActionOnSubscription
from app.utils import join_clients_and_subscriptions, build_entries_to_display_subscriptions, \
    get_subscription_log_to_display
from app.models import User, Subscription, SubscriptionAction, SubscriptionLog, SubscriptionType, Client, \
     ClientToSubscription, Application, ApplicationToClient, Discount

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    #: find subscriptions module
    find_subscriptions_by_name_form = FindSubscriptionByName()
    find_subscriptions_by_barcode_form = FindSubscriptionByBarcode()
    subscriptions_to_display = build_entries_to_display_subscriptions(False)
    subscription_log_to_display = get_subscription_log_to_display(False)
    #: query to get current subscriptions' holders
    name_choices = [row.Client.full_name for row in join_clients_and_subscriptions().all()]
    #: removing duplicates
    name_choices = list(dict.fromkeys(name_choices))
    if find_subscriptions_by_name_form.start_search_by_name.data and find_subscriptions_by_name_form.validate():
        query = join_clients_and_subscriptions()\
                .filter(Client.full_name == find_subscriptions_by_name_form.full_name.data)
        subscription_log_to_display = get_subscription_log_to_display(query)
        subscriptions_to_display = build_entries_to_display_subscriptions(query)
    if find_subscriptions_by_barcode_form.start_search_by_barcode.data and find_subscriptions_by_barcode_form.validate():
        query = join_clients_and_subscriptions()\
                .filter(Client.barcode == find_subscriptions_by_barcode_form.barcode.data)
        subscription_log_to_display = get_subscription_log_to_display(query)
        subscriptions_to_display = build_entries_to_display_subscriptions(query)

    #: perform actions on subscriptions module
    perform_action_form = PerformActionOnSubscription()
    perform_action_form.subscription_id.choices = [(n, n) for n in subscriptions_to_display['Номер абонемента']]
    perform_action_form.actions.choices = [(a.subscription_action_id, a.name) for a in SubscriptionAction.query.all()]
    if perform_action_form.submit_action.data:
        #: when POST request for action on subscription is sent,
        #: data in perform_action_form.subscription_id.choices is being flashed causing validation error
        #: to fix this we need to populate it with some value
        perform_action_form.subscription_id.choices = [(perform_action_form.subscription_id.data, perform_action_form.subscription_id.data)]
        if perform_action_form.validate():
            subscription = Subscription.query.get(perform_action_form.subscription_id.data)
            if subscription is not None:
                flash(subscription.perform_action_by_id(perform_action_form.actions.data,
                                                        current_user,
                                                        perform_action_form.optional_argument.data))
            else:
                flash('Такой абонемент не найден')

    return render_template('mainpage/mainpage.html', title='Центр управления посетителями',
                           find_subscriptions_by_name_form=find_subscriptions_by_name_form,
                           name_choices=name_choices,
                           find_subscriptions_by_barcode_form=find_subscriptions_by_barcode_form,
                           subscriptions_to_display=subscriptions_to_display,
                           subscription_log_to_display=subscription_log_to_display,
                           perform_action_form=perform_action_form,
                           perform_action_form_table_title=u'Сотворить действие над абонементом',
                           )
