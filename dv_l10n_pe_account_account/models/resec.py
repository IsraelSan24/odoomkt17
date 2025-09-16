# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.date_utils import get_month, get_fiscal_year
from odoo.tools.misc import format_date

import re
from collections import defaultdict
import json

import logging
_logger = logging.getLogger(__name__)

class ReSequenceWizard(models.TransientModel):
    _inherit = 'account.resequence.wizard'

    @api.depends('first_name', 'move_ids', 'sequence_number_reset')
    def _compute_new_values(self):
        """Compute the proposed new values.

        Sets a json string on new_values representing a dictionary thats maps account.move
        ids to a disctionay containing the name if we execute the action, and information
        relative to the preview widget.
        """
        def _get_move_key(move_id):
            if self.sequence_number_reset == 'year':
                return move_id.date.year
            elif self.sequence_number_reset == 'month':
                return (move_id.date.year, move_id.date.month)
            return 'default'

        self.new_values = "{}"
        for record in self.filtered('first_name'):
            moves_by_period = defaultdict(lambda: record.env['account.move'])
            for move in record.move_ids._origin:  # Sort the moves by period depending on the sequence number reset
                moves_by_period[_get_move_key(move)] += move

            format, format_values = self.env['account.move']._get_sequence_format_param(record.first_name)
            format = "{prefix1}{seq:0{seq_length}d}{suffix}"
            _logger.info('format: %s', format)
            _logger.info('format_values: %s', format_values)
            new_values = {}
            for j, period_recs in enumerate(moves_by_period.values()):
                # compute the new values period by period
                for move in period_recs:
                    new_values[move.id] = {
                        'id': move.id,
                        'current_name': move.name,
                        'state': move.state,
                        'date': format_date(self.env, move.date),
                        'server-date': str(move.date),
                    }
                    _logger.info('new_values: %s', new_values)
                new_name_list = [format.format(**{
                    **format_values,
                    'year': period_recs[0].date.year % (10 ** format_values['year_length']),
                    'month': period_recs[0].date.month,
                    'seq': i + (format_values['seq'] if j == (len(moves_by_period)-1) else 1),
                }) for i in range(len(period_recs))]
                
                # For all the moves of this period, assign the name by increasing initial name
                for move, new_name in zip(period_recs.sorted(lambda m: (m.sequence_prefix, m.sequence_number)), new_name_list):
                    new_values[move.id]['new_by_name'] = new_name
                # For all the moves of this period, assign the name by increasing date
                for move, new_name in zip(period_recs.sorted(lambda m: (m.date, m.name, m.id)), new_name_list):
                    new_values[move.id]['new_by_date'] = new_name

            record.new_values = json.dumps(new_values)
            
    @api.depends('first_name')
    def _compute_sequence_number_reset(self):
        for record in self:
            _logger.info('first_name')
            _logger.info(record.first_name)
            sequence_number_reset = record.move_ids[0]._deduce_sequence_number_reset(record.first_name)
            _logger.info('sequence_number_reset')
            _logger.info(sequence_number_reset)
            record.sequence_number_reset = sequence_number_reset

    @api.depends('move_ids')
    def _compute_first_name(self):
        self.first_name = ""
        for record in self:
            if record.move_ids:
                record.first_name = min(record.move_ids._origin.mapped('name'))
                
    @api.depends('new_values', 'ordering')
    def _compute_preview_moves(self):
        """Reduce the computed new_values to a smaller set to display in the preview."""
        for record in self:
            _logger.info("record.new_values")
            _logger.info(record.new_values)
            new_values = sorted(json.loads(record.new_values).values(), key=lambda x: x['server-date'], reverse=True)
            changeLines = []
            in_elipsis = 0
            previous_line = None
            for i, line in enumerate(new_values):
                if i < 3 or i == len(new_values) - 1 or line['new_by_name'] != line['new_by_date'] \
                 or (self.sequence_number_reset == 'year' and line['server-date'][0:4] != previous_line['server-date'][0:4])\
                 or (self.sequence_number_reset == 'month' and line['server-date'][0:7] != previous_line['server-date'][0:7]):
                    if in_elipsis:
                        changeLines.append({'id': 'other_' + str(line['id']), 'current_name': _('... (%s other)', in_elipsis), 'new_by_name': '...', 'new_by_date': '...', 'date': '...'})
                        in_elipsis = 0
                    
                    _logger.info("previous_line")
                    _logger.info(previous_line)
                    _logger.info("line")
                    _logger.info(line)
                    changeLines.append(line)
                else:
                    in_elipsis += 1
                previous_line = line
            _logger.info("changeLines")
            _logger.info(changeLines)
            
            record.preview_moves = json.dumps({
                'ordering': record.ordering,
                'changeLines': changeLines,
            })