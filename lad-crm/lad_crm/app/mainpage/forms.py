from app import db
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, DecimalField, TextAreaField, \
     SelectField, DateField, FileField
from wtforms.validators import ValidationError, DataRequired, Email, Length, Optional
from app.models import User, Subscription, SubscriptionAction, SubscriptionLog, SubscriptionType, Client, \
     ClientToSubscription, Application, ApplicationToClient, Discount
from app.utils import join_clients_and_subscriptions


class PerformActionOnSubscription(FlaskForm):
    subscription_id = SelectField("Номер абонемента", coerce=int)
    actions = SelectField(u'Действие', coerce=int)
    optional_argument = IntegerField(u'Дополнительный аргумент', validators=[Optional()])
    submit_action = SubmitField(u'Применить!')


class FindSubscriptionByBarcode(FlaskForm):
    barcode = IntegerField("Штрих-код", validators=[DataRequired()])
    start_search_by_barcode = SubmitField("Искать по штрих-коду")


class FindSubscriptionByName(FlaskForm):
    full_name = StringField("ФИО", validators=[DataRequired()])
    start_search_by_name = SubmitField("Искать по ФИО")

    def validate_full_name(self, full_name):
        client = Client.query.filter_by(full_name=full_name.data).first()
        if client is None:
            raise ValidationError('Человека с таким именем нет в базе')
        query = join_clients_and_subscriptions()
        query = query.filter(Client.full_name == full_name.data)
        if not query.all():
            raise ValidationError('У этого человека нет неархивных абонементов')


class AddSubscription(FlaskForm):
    barcode = IntegerField("Штрих-код", validators=[Optional()])
    full_name = StringField("Владелец", validators=[DataRequired(), Length(max=100)])
    subscription_type = SelectField("Тип абонемента", coerce=int)
    discount_type = SelectField("Скидка", coerce=int)
    price = IntegerField("Цена", validators=[DataRequired()])
    debt = IntegerField("Долг", validators=[Optional()])
    visit_number = IntegerField("Число посещений", validators=[DataRequired()])
    active_up_to = DateField("Действует до", validators=[DataRequired()])
    comment = TextAreaField("Комментарий", validators=[Length(max=500)])
    add_as_new_client = BooleanField("Добавить также новую запись в базу клиентов")
    submit_subscription = SubmitField("Добавить абонемент")

    #: if we are not supposed to also add a new client
    #: check if client with such full name exists
    #: and if we are
    #: check if there are at least first and last names in full name, i.e. 2 words in full name
    def validate_full_name(self, full_name):
        if not self.add_as_new_client.data:
            client = Client.query.filter_by(full_name=full_name.data).first()
            if client is None:
                raise ValidationError('Ошибка добавления нового абонемента: человека с таким полным именем нет в базе.')
        else:
            names = full_name.data.split()
            if len(names) <= 1:
                raise ValidationError("ФИО должно включать как минимум фамилию и имя (через пробел).")

    #: if we are supposed to also add a new client
    #: then check if the barcode is not in use first
    def validate_barcode(self, barcode):
        if self.add_as_new_client.data and barcode.data is not None:
            client = Client.query.filter_by(barcode=barcode.data).first()
            if client is not None:
                raise ValidationError('Ошибка добавления нового клиента в базу: штрих-код уже зарегистрирован за другим человеком.')


class AddClient(FlaskForm):
    first_name = StringField("Имя", validators=[DataRequired(), Length(max=50)])
    last_name = StringField("Фамилия", validators=[DataRequired(), Length(max=100)])
    middle_name = StringField("Отчество", validators=[Length(max=100)])
    birthday = DateField("День рождения", validators=[Optional()])
    email = StringField("Почта", validators=[Email(), Length(max=100), Optional()])
    phone = StringField("Телефон (в формате 8-999-999-99-99)", validators=[Length(max=20)])
    additional_info = TextAreaField("Дополнительная информация", validators=[Length(max=500)])
    allow_email_notifications = BooleanField("Уведомления по почте")
    allow_phone_notifications = BooleanField("Уведомления по телефону")
    barcode = IntegerField("Штрих-код", validators=[Optional()])
    in_relations_with = StringField("Связанный с ним", validators=[Length(max=100)])
    comment = TextAreaField("Текущий комментарий", validators=[Length(max=500)])
    application_id = IntegerField("Номер заявления", validators=[Optional()])
    image = FileField("Фото заявления")
    submit_client = SubmitField("Добавить в базу")


    def validate_barcode(self, barcode):
        if barcode is not None:
            client = Client.query.filter_by(barcode=barcode.data).first()
            if client is not None:
                raise ValidationError('Штрих-код уже зарегистрирован.')


class PerformAction(FlaskForm):
    subscription_id = IntegerField(u'Номер абонемента', validators=[DataRequired()])
    actions = SelectField(u'Действие', coerce=int)
    submit_action = SubmitField(u'Действовать!')