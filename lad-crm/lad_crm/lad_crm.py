from app import create_app, db
from app.models import User, Subscription, SubscriptionAction, SubscriptionLog, SubscriptionType, Client, \
     ClientToSubscription, Application, ApplicationToClient, Discount

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Subscription': Subscription, 'SubscriptionAction': SubscriptionAction,
            'SubscriptionLog': SubscriptionLog, 'SubscriptionType': SubscriptionType, 'Client': Client,
            'ClientToSubscription': ClientToSubscription, 'Application': Application,
            'ApplicationToClient': ApplicationToClient, 'Discount': Discount}
