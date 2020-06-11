from flask import render_template, flash, redirect, url_for
from app import db
from app.managedb import bp
from app.managedb.forms import AddSubscriptionType, AddDiscountType, AddSubscriptionActionType, AddSubscription, \
     AddClient, EditClient, PerformAction
from flask_login import current_user, login_required
from app.models import User, Subscription, SubscriptionAction, SubscriptionLog, SubscriptionType, Client, \
     ClientToSubscription, Application, ApplicationToClient, Discount
import json
from app.utils import join_clients_and_subscriptions, build_entries_to_display_subscriptions, \
    disconnect_client_from_his_applications




@bp.route('/managedb')
@login_required
def managedb():
    return redirect(url_for('managedb.subscriptions'))


@bp.route('/managedb/service', methods=['GET', 'POST'])
@login_required
def service():

    #: code below is for handling subscription type creation form and displaying available subscription types
    subscription_types = SubscriptionType.query.all()
    subscription_type_creation_form = AddSubscriptionType()
    if subscription_type_creation_form.submit_subscription_type.data and subscription_type_creation_form.validate():
        new_subscription_type = SubscriptionType(name=subscription_type_creation_form.name.data, price=subscription_type_creation_form.price.data, \
                                                 visit_number=subscription_type_creation_form.visit_number.data, \
                                                 active_period=subscription_type_creation_form.active_period.data, freeze_period=subscription_type_creation_form.freeze_period.data)
        db.session.add(new_subscription_type)
        db.session.commit()
        flash('Добавлен новый вид абонемента: {}'.format(subscription_type_creation_form.name.data))

    #: code below is for handling discount type creation form and displaying available discount types
    discount_types = Discount.query.all()
    discount_creation_form = AddDiscountType()
    if discount_creation_form.submit_discount_type.data and discount_creation_form.validate():
        new_discount_type = Discount(name=discount_creation_form.name.data, description=discount_creation_form.description.data, value=discount_creation_form.value.data)
        db.session.add(new_discount_type)
        db.session.commit()
        flash('Добавлен новый вид абонемента: {}'.format(discount_creation_form.name.data))

    #: code below is for subscription action creation form and displaying subscription actions
    subscription_action_types = SubscriptionAction.query.all()
    subscription_action_creation_form = AddSubscriptionActionType()
    if subscription_action_creation_form.submit_subscription_action_type.data and subscription_action_creation_form.validate():
        details_template_as_dict = json.loads(subscription_action_creation_form.details_template.data)
        new_subscription_action_type = SubscriptionAction(name=subscription_action_creation_form.name.data, details_template=details_template_as_dict)
        db.session.add(new_subscription_action_type)
        db.session.commit()
        flash('Добавлен новый вид действия над абонементом: {}'.format(subscription_action_creation_form.name.data))

    return render_template('managedb/service.html',
                           subscription_type_creation_form=subscription_type_creation_form,
                           subscription_type_creation_form_table_title=u'Добавить новый тип абонемента',
                           subscription_types=subscription_types,
                           discount_creation_form=discount_creation_form,
                           discount_creation_form_table_title=u'Добавить новый вид скидки',
                           discount_types=discount_types,
                           subscription_action_creation_form=subscription_action_creation_form,
                           subscription_action_creation_form_table_title=u'Добавить новый вид действия над абонементом',
                           subscription_action_types=subscription_action_types)


@bp.route('/managedb/clients', methods=['GET', 'POST'])
@login_required
def clients():

    #: code below is for adding new client, handling client creation form, and displaying clients present in the db
    clients = Client.query.all()
    client_creation_form = AddClient()
    if client_creation_form.submit_client.data and client_creation_form.validate():
        #: checking if the person has a middle name and concatenating full name based on it
        if client_creation_form.middle_name.data:
            full_name = client_creation_form.last_name.data + " " + client_creation_form.first_name.data + " " + client_creation_form.middle_name.data
        else:
            full_name = client_creation_form.last_name.data + " " + client_creation_form.first_name.data
        new_client = Client(first_name=client_creation_form.first_name.data, last_name=client_creation_form.last_name.data, \
                            middle_name=client_creation_form.middle_name.data, full_name=full_name, birthday=client_creation_form.birthday.data, email=client_creation_form.email.data, \
                            phone=client_creation_form.phone.data, additional_info=client_creation_form.additional_info.data, \
                            allow_email_notifications=client_creation_form.allow_email_notifications.data, allow_phone_notifications=client_creation_form.allow_phone_notifications.data, \
                            barcode=client_creation_form.barcode.data, comment=client_creation_form.comment.data, in_relations_with=client_creation_form.in_relations_with.data)
        db.session.add(new_client)
        db.session.commit()
        flash('В базу добавлен новый посетитель: {}'.format(full_name))
        #: managing application
        #: a) there is no application with such number existing -> creating new entry
        if Application.query.get(client_creation_form.application_id.data) is None:
            #: if image is uploaded, i.e. string containing path is not empty
            if client_creation_form.image.data:
                #: to do >> managing file upload
                print(client_creation_form.image.data)
                application = Application(application_id=client_creation_form.application_id.data)
                db.session.add(application)
                db.session.commit()
                flash('Добавлено новое заявление (c фото) номер: {}'.format(client_creation_form.application_id.data))
            else:
                application = Application(application_id=client_creation_form.application_id.data)
                db.session.add(application)
                db.session.commit()
                flash('Добавлено новое заявление (без фото) номер: {}'.format(client_creation_form.application_id.data))
        #: b) there is an application with such number -> just fetch it
        else:
            application = Application.query.get(client_creation_form.application_id.data)
        #: when application exists connect client and his application
        client_to_application_connection = ApplicationToClient(client_id=new_client.client_id, application_id=application.application_id)
        db.session.add(client_to_application_connection)
        db.session.commit()
        flash('Добавлена связь между {} и заявлением номер {}'.format(full_name, client_creation_form.application_id.data))

    return render_template('managedb/clients.html',
                           client_creation_form=client_creation_form,
                           client_creation_form_table_title=u'Добавить человека в базу',
                           clients=clients)


@bp.route('/managedb/subscriptions', methods=['GET', 'POST'])
@login_required
def subscriptions():
    #: subscription creation
    query = join_clients_and_subscriptions()
    subscriptions = build_entries_to_display_subscriptions(query)
    subscription_creation_form = AddSubscription()
    subscription_creation_form.full_name.datalist = [c.full_name for c in Client.query.all()]
    subscription_creation_form.subscription_type.choices = [(st.subscription_type_id, st.name) for st in SubscriptionType.query.filter_by(is_archived=False).order_by('name')]
    subscription_creation_form.discount_type.choices = [(d.discount_id, d.name) for d in Discount.query.filter_by(is_archived=False).order_by('name')]
    if subscription_creation_form.submit_subscription.data and subscription_creation_form.validate():
        if subscription_creation_form.add_as_new_client.data:
            #: client is needed to be created
            names = subscription_creation_form.full_name.data.split()
            if len(names) == 2:
                first_name = names[1]
                last_name = names[0]
                middle_name = None
                full_name = last_name + " " + first_name
            else:
                first_name = names[1]
                last_name = names[0]
                middle_name = names[2]
                full_name = last_name + " " + first_name + " " + middle_name
            client = Client(first_name=first_name,
                            last_name=last_name,
                            middle_name=middle_name,
                            full_name=full_name,
                            barcode=client_creation_form.barcode.data)
            db.session.add(client)
            db.session.commit()
            flash('В базу добавлен новый посетитель: {}'.format(full_name))
        else:
            #: client already exists
            #: to do: manage situations with full namesakes
            client = Client.query.filter_by(full_name=subscription_creation_form.full_name.data).first()
        #: if there is no discount, we must pass None to discount_id
        #: fix this by adding "No discount" entry into discount table
        new_subscription = Subscription(subscription_type_id=subscription_creation_form.subscription_type.data,
                                        discount_id=subscription_creation_form.discount_type.data,
                                        created_by=current_user.user_id,
                                        price=subscription_creation_form.price.data,
                                        debt=subscription_creation_form.debt.data,
                                        visit_number=subscription_creation_form.visit_number.data,
                                        active_up_to=subscription_creation_form.active_up_to.data,
                                        comment=subscription_creation_form.comment.data)
        db.session.add(new_subscription)
        db.session.commit()
        client_to_subscription = ClientToSubscription(client_id=client.client_id, subscription_id=new_subscription.subscription_id)
        db.session.add(client_to_subscription)
        db.session.commit()
        flash("Добавлен абонемент {} на {}, добавлен клиент в базу:{}".format(subscription_creation_form.full_name.data,
                                                                              SubscriptionType.query.get(subscription_creation_form.subscription_type.data).name,
                                                                              subscription_creation_form.add_as_new_client.data))

    #: doing some actions on subscriptions
    perform_action_form = PerformAction()
    perform_action_form.actions.choices = [(a.subscription_action_id, a.name) for a in SubscriptionAction.query.all()]
    if perform_action_form.submit_action.data and perform_action_form.validate():
        subscription = Subscription.query.get(int(perform_action_form.subscription_id.data))
        if subscription is not None:
            flash(subscription.perform_template_action_by_id(perform_action_form.actions.data, current_user))
        else:
            flash('Такой абонемент не найден')

    return render_template('managedb/subscriptions.html',
                           subscription_creation_form=subscription_creation_form,
                           subscription_creation_form_table_title=u'Добавить абонемент в базу',
                           subscriptions=subscriptions,
                           perform_action_form=perform_action_form,
                           perform_action_form_table_title=u'Сделать что-то с абонементом')

@bp.route('/managedb/subscriptions/delete/<subscription_id>', methods=['GET', 'POST'])
@login_required
def delete_subscription(subscription_id):
    #: to do > add check if user is permitted to do the action
    subscription = Subscription.query.get(int(subscription_id))
    if subscription.actions_performed.all():
        flash("По этому абонементу проводились действия, в целях сохранения целостности базы удалить его нельзя")
        return redirect(url_for('managedb.subscriptions'))
    db.session.delete(subscription.client.first())
    db.session.delete(subscription)
    db.session.commit()
    flash("Абонемент {} удален".format(subscription))
    return redirect(url_for('managedb.subscriptions'))

@bp.route('/managedb/subscriptions/edit/<subscription_id>', methods=['GET', 'POST'])
@login_required
def edit_subscription(subscription_id):
    #: to do > add check if user is permitted to do the action
    subscription = Subscription.query.get(int(subscription_id))
    subscription_edit_form = AddSubscription()
    subscription_edit_form.subscription_type.choices = [(st.subscription_type_id, st.name) for st in SubscriptionType.query.filter_by(is_archived=False).order_by('name')]
    subscription_edit_form.discount_type.choices = [(d.discount_id, d.name) for d in Discount.query.filter_by(is_archived=False).order_by('name')]
    subscription_edit_form.full_name.datalist = [c.full_name for c in Client.query.all()]

    if subscription_edit_form.submit_subscription.data and subscription_edit_form.validate():
        if subscription_edit_form.add_as_new_client.data:
            #: client is needed to be created
            names = subscription_edit_form.full_name.data.split()
            if len(names) == 2:
                first_name = names[1]
                last_name = names[0]
                middle_name = None
                full_name = last_name + " " + first_name
            else:
                first_name = names[1]
                last_name = names[0]
                middle_name = names[2]
                full_name = last_name + " " + first_name + " " + middle_name
            client = Client(first_name=first_name,
                            last_name=last_name,
                            middle_name=middle_name,
                            full_name=full_name,
                            barcode=subscription_edit_form.barcode.data)
            db.session.add(client)
            db.session.commit()
            flash('В базу добавлен новый посетитель: {}'.format(full_name))
            subscription.client.first().client_id = client.client_id
        else:
            #: client already exists
            if subscription_edit_form.full_name.data != subscription.client.first().owner.full_name:
                #: if client changed - > change also a SubscriptionToClient entry
                client = Client.query.filter_by(full_name=subscription_edit_form.full_name.data).first()
                subscription.client.first().client_id = client.client_id
        #: update subscription
        subscription.subscription_type_id = subscription_edit_form.subscription_type.data
        subscription.discount_id = subscription_edit_form.discount_type.data
        subscription.price = subscription_edit_form.price.data
        subscription.debt = subscription_edit_form.debt.data
        subscription.visit_number = subscription_edit_form.visit_number.data
        subscription.active_up_to = subscription_edit_form.active_up_to.data
        subscription.comment = subscription_edit_form.comment.data
        db.session.commit()

        flash("Абонемент {} изменен".format(subscription))
        return redirect(url_for('managedb.subscriptions'))

    subscription_edit_form.subscription_type.default = subscription.subscription_type_id
    subscription_edit_form.discount_type.default = subscription.discount_id
    subscription_edit_form.process()
    subscription_edit_form.barcode.data = subscription.client.first().owner.barcode
    subscription_edit_form.full_name.default = subscription.client.first().owner.full_name
    subscription_edit_form.price.data = int(subscription.price)
    subscription_edit_form.debt.data = int(subscription.debt)
    subscription_edit_form.visit_number.data = int(subscription.visit_number)
    subscription_edit_form.active_up_to.data = subscription.active_up_to
    subscription_edit_form.comment.data = subscription.comment

    return render_template('managedb/edit_subscription.html',
                           subscription_edit_form=subscription_edit_form,
                           subscription_edit_form_table_title=u'Редактирование записи об абонементе',
                           )


@bp.route('/managedb/clients/delete/<client_id>', methods=['GET', 'POST'])
@login_required
def delete_client(client_id):
    #: to do > add check if user is permitted to do the action
    client = Client.query.get(int(client_id))
    if client.subscriptions.all():
        flash("Клиент покупал абонементы, в целях сохранения целостности базы удалить его нельзя")
        return redirect(url_for('managedb.clients'))
    disconnect_client_from_his_applications(client)
    db.session.delete(client)
    db.session.commit()
    flash("Запись {} удалена всместе со связанными заявлениями (если они не были привязаны к кому-то ещё)".format(client))
    return redirect(url_for('managedb.clients'))


@bp.route('/managedb/clients/edit/<client_id>', methods=['GET', 'POST'])
@login_required
def edit_client(client_id):
    #: to do > add check if user is permitted to do the action
    #: to do > manage image
    client = Client.query.get(int(client_id))
    client_edit_form = EditClient()
    client_data = [
        client.first_name,
        client.last_name,
        client.middle_name,
        client.birthday,
        client.email,
        client.phone,
        client.additional_info,
        client.allow_email_notifications,
        client.allow_phone_notifications,
        client.barcode,
        client.in_relations_with,
        client.comment,
        client.applications.first().application_id if client.applications.first() else None,
    ]
    if client_edit_form.submit_client.data and client_edit_form.validate():
        if client_edit_form.application_id.data != client_data[12]:
            #: if client's application id changed
            #: delete old application to client connection
            disconnect_client_from_his_applications(client)
            #: a) there is no application with such number existing -> creating new entry
            if Application.query.get(client_edit_form.application_id.data) is None:
                #: if image is uploaded, i.e. string containing path is not empty
                if client_edit_form.image.data:
                    #: to do >> managing file upload
                    print(client_edit_form.image.data)
                    application = Application(application_id=client_edit_form.application_id.data)
                    db.session.add(application)
                    flash(
                        'Добавлено новое заявление (c фото) номер: {}'.format(client_edit_form.application_id.data))
                else:
                    application = Application(application_id=client_edit_form.application_id.data)
                    db.session.add(application)
                    flash('Добавлено новое заявление (без фото) номер: {}'.format(
                        client_edit_form.application_id.data))

            #: b) there is an application with such number -> just fetch it
            else:
                application = Application.query.get(client_edit_form.application_id.data)
            #: when application exists connect client and his application
            client_to_application_connection = ApplicationToClient(client_id=client.client_id,
                                                                   application_id=application.application_id)
            db.session.add(client_to_application_connection)
            flash('Добавлена связь между {} и заявлением номер {}'.format(client.full_name,
                                                                          client_edit_form.application_id.data))
        #: checking if the person has a middle name and concatenating full name based on it
        if client_edit_form.middle_name.data:
            full_name = client_edit_form.last_name.data + " " + client_edit_form.first_name.data + " " + client_edit_form.middle_name.data
        else:
            full_name = client_edit_form.last_name.data + " " + client_edit_form.first_name.data
        #: updating client entry
        client.full_name = full_name
        client.first_name = client_edit_form.first_name.data
        client.last_name = client_edit_form.last_name.data
        client.middle_name = client_edit_form.middle_name.data
        client.birthday = client_edit_form.birthday.data
        client.email = client_edit_form.email.data
        client.phone = client_edit_form.phone.data
        client.additional_info = client_edit_form.additional_info.data
        client.allow_email_notifications = client_edit_form.allow_email_notifications.data
        client.allow_phone_notifications = client_edit_form.allow_phone_notifications.data
        client.barcode = client_edit_form.barcode.data
        client.in_relations_with = client_edit_form.in_relations_with.data
        client.comment = client_edit_form.comment.data
        flash('Изменена запись: {}'.format(full_name))
        db.session.commit()
        return redirect(url_for('managedb.clients'))

    for field, c_data in zip(client_edit_form, client_data):
        if field.name not in ["Фото заявления", "Добавить в базу"]:
            field.data = c_data

    return render_template('managedb/edit_client.html',
                           client_edit_form=client_edit_form,
                           client_edit_form_table_title=u'Редактирование записи о клиенте',
                           )

