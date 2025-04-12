from django.apps import AppConfig
import threading
import time

import threading
import time
from datetime import date

class PrintDjangoThread(threading.Thread):
    def __init__(self, interval=1):  # interval in seconds
        super().__init__()
        self.interval = interval
        self.running = True

    def run(self):
        from ems_app.models import Subscription, InvoiceTable  # Import inside to ensure apps are ready
        while self.running:
            #print("Checking invoice statuses...")
            active_subs = Subscription.objects.filter(status="Active", deactive__isnull=True)
            for sub in active_subs:
                # Get latest invoice for this subscription (if multiple exist)
                invoice = InvoiceTable.objects.filter(subscription=sub).order_by('-end_date').first()
                if invoice:
                    if invoice.status == "Paid":
                        continue
                    else:
                        current_date = date.today()
                        print(invoice.end_date)
                        print(current_date)
                        if invoice.end_date >= current_date:
                            print(f"Subscription {sub.sub_id}: this id is stop")
                            sub.deactive = invoice.end_date
                            sub.status = "Deactive"
                            sub.save()
                        else:
                            print(f"Subscription {sub.sub_id}: time continue")
                else:
                    print(f"Subscription {sub.sub_id}: No invoice found")

            time.sleep(self.interval)

    def stop(self):
        self.running = False



class EmsAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ems_app"

    def ready(self):
          # Start the thread when Django app is ready
          thread = PrintDjangoThread(interval=1)
          thread.start()
