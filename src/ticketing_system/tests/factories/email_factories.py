import factory

from ticketing_system.emails.models import Email


class EmailFactory(factory.django.DjangoModelFactory):

    """
    Factory for creating instances of the Email model.
    """

    class Meta:
        model = Email

    status = Email.Status.READY
    from_email = factory.Faker("email")
    to_email = factory.Faker("email")
    subject = factory.Faker("sentence", nb_words=5)
    message = factory.Faker("text")
    html = factory.Faker("text")
    sent_at = factory.Maybe(
        factory.LazyAttribute(lambda obj: obj.status == Email.Status.SENT),
        factory.Faker("date_time"),
        None,
    )

