import json
import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class IgmFsmApiController(http.Controller):

    def _json_body(self):
        data = request.httprequest.get_data(as_text=True) or '{}'
        return json.loads(data)

    def _idempotent(self, key, endpoint, func):
        Store = request.env['igm.fsm.api.request'].sudo()
        if key:
            existing = Store.search([('igm_key', '=', key)], limit=1)
            if existing and existing.igm_result:
                return json.loads(existing.igm_result)
        result = func()
        if key:
            try:
                with request.env.cr.savepoint():
                    Store.create({
                        'igm_key': key,
                        'igm_endpoint': endpoint,
                        'igm_user_id': request.env.uid,
                        'igm_result': json.dumps(result),
                    })
            except Exception:
                pass
        return result

    @http.route('/igm/api/fsm/tasks/mine', type='http', auth='user', methods=['GET', 'POST'], csrf=False, cors='*')
    def tasks_mine(self, **kw):
        try:
            tasks = request.env['project.task'].igm_fsm_api_get_my_tasks()
            return request.make_json_response(tasks)
        except Exception as e:
            _logger.exception("igm_fsm_api tasks/mine failed")
            return request.make_json_response({'status': 'error', 'message': str(e)}, status=500)

    @http.route('/igm/api/fsm/task/done', type='http', auth='user', methods=['POST'], csrf=False, cors='*')
    def task_done(self, **kw):
        task_id = None
        try:
            body = self._json_body()
            task_id = int(body['taskId'])
            worked = body.get('workedHours')
            key = body.get('idempotencyKey')

            def run():
                task = request.env['project.task'].browse(task_id)
                task.check_access('write')
                task.igm_fsm_api_mark_done(worked_hours=worked)
                return {'status': 'ok', 'taskId': task_id}

            return request.make_json_response(self._idempotent(key, 'task/done', run))
        except Exception as e:
            _logger.exception("igm_fsm_api task/done failed")
            return request.make_json_response({'status': 'error', 'taskId': task_id, 'message': str(e)}, status=500)

    @http.route('/igm/api/fsm/task/photo', type='http', auth='user', methods=['POST'], csrf=False, cors='*')
    def task_photo(self, **kw):
        task_id = None
        try:
            body = self._json_body()
            task_id = int(body['taskId'])
            image = body['imageBase64']
            note = body.get('note')
            key = body.get('idempotencyKey')

            def run():
                task = request.env['project.task'].browse(task_id)
                task.check_access('write')
                task.igm_fsm_api_add_photo(image, note=note)
                return {'status': 'ok', 'taskId': task_id}

            return request.make_json_response(self._idempotent(key, 'task/photo', run))
        except Exception as e:
            _logger.exception("igm_fsm_api task/photo failed")
            return request.make_json_response({'status': 'error', 'taskId': task_id, 'message': str(e)}, status=500)
