# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api, SUPERUSER_ID
from openerp.exceptions import Warning


class BaseWorkflowPolicyObject(models.AbstractModel):
    _name = "base.workflow_policy_object"
    _description = "Workflow Policy Object"

    @api.multi
    def _compute_policy(self):
        obj_line = self.env["base.workflow_policy_line"]
        criteria = [
            ("workflow_id.model_id.model", "=", str(self._model)),
        ]
        policy_lines = obj_line.search(criteria)
        for document in self:
            for policy in policy_lines:
                if self.env.user.id == SUPERUSER_ID:
                    result = True
                    raise Warning("a")
                else:
                    result = policy.\
                        get_policy(
                            document)
                setattr(
                    document,
                    policy.field_id.name,
                    result,
                )
