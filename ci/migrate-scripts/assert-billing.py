# Copyright © Michal Čihař <michal@weblate.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Billing migration testing."""

from weblate.trans.models import Project

project = Project.objects.get(pk=1)
assert project.billing.owners.filter(username="billingtest").exists()
