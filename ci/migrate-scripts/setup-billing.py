# Copyright © Michal Čihař <michal@weblate.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Billing migration testing."""

from weblate.auth.models import User, setup_project_groups
from weblate.billing.models import Billing, Plan
from weblate.trans.models import Project

plan = Plan.objects.create(name="Basic plan", price=19, yearly_price=199)
billing = Billing.objects.create(plan=plan)
project = Project.objects.get(pk=1)
setup_project_groups(sender=Project, instance=project, created=True)
billing.projects.add(project)
user = User.objects.create(username="billingtest")
project.add_user(user, "Billing")
