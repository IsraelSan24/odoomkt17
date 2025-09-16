from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class Gallery(models.Model):
    _name = 'gallery'
    _description = 'Photo Gallery'
    _order = 'id desc'

    name = fields.Char(copy=False, required=True, default=lambda self: _('New'))
    user_id = fields.Many2one(comodel_name="res.users", string="Responsible",
                              index=True, default=lambda self: self.env.user)
    product_id = fields.Many2one(comodel_name="product.template", string="Product")
    product_image = fields.Image(
        string="Photo",
        related="product_id.image_1920",
        store=True,
        readonly=True
    )
    date = fields.Datetime(string="Date", default=fields.Datetime.now, required=True)


    def button_duplicate_product(self):
        product_list_ids = []
        gallery_duplicated = ""
        gallery_ids = self.env['gallery'].search([('id','!=',self.id)])
        for rec in gallery_ids:
            product_list_ids.append(rec.product_id.id)
            if rec.product_id.id == self.product_id.id:
                gallery_duplicated += (rec.name + " ")
        if self.product_id.id in list(filter(None, product_list_ids)):
            raise ValidationError(_("""
                                    The selected product has already been registered. Review: %s \n
                                    Please, choose a diferent product and verify that it is not in use.\n
                                    If you don't want to choose another product, leave the product field empty.
                                """) % (gallery_duplicated))
        else:
            raise ValidationError(_("Everything's fine!"))


    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('gallery') or _('New')
        return super(Gallery, self).create(vals)