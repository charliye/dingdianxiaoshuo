from .sql import Sql
from dingdian.items import DingdianItem
from dingdian.items import DcontentItem

class DingdianPipeline(object):
    def process_item(self, item, spider):
        if isinstance(item, DingdianItem):
            name_id = item['name_id']
            ret = Sql.select_name(name_id)
            if ret[0] == 1:
                print('It is already exist.')
                pass
            else:
                xs_name = item['name']
                xs_author = item['author']
                category = item['category']
                Sql.insert_dd_name(xs_name, xs_author, category, name_id)
                print('Start store novel title')

        if isinstance(item, DcontentItem):
            url = item['chapterurl']
            name_id = item['id_name']
            num_id = item['num']
            xs_chaptername = item['chaptername']
            xs_content = item['chaptercontent']
            Sql.insert_dd_chaptername(xs_chaptername, xs_content, name_id, num_id, url)
            print('Store successfully!')
            return item
