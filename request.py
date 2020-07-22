from misc import read_yaml
import datetime
from ebaysdk.exception import ConnectionError
from ebaysdk.finding import Connection

conf = read_yaml('./conf.yaml')
api_info = read_yaml(conf['api_config_path'])


def query(**kwargs):
    try:
        api = Connection(appid=api_info['appid'], config_file=None)
        response = api.execute('findItemsAdvanced', kwargs)
        assert(response.reply.ack == 'Success')
        assert(type(response.reply.timestamp) == datetime.datetime)
        assert(type(response.reply.searchResult.item) == list)
        full_items = response.reply.searchResult.item
        assert(type(response.dict()) == dict)
        print(full_items)
        return full_items
    except ConnectionError as e:
        print(e)
        print(e.response.dict())
        return e

# Not working for now...
# res = query(keywords='Super Smash Brothers Melee')
# print(res[0])
# from ebaysdk.soa.finditem import Connection as FindItem
# try:
#     api = FindItem(consumer_id=api_info['appid'], config_file=conf['api_config_path'])
#     print(res[0].itemId)
#     api.find_items_by_ids([res[0].itemId])
# except Exception as exc:
#     print(exc)
#     print(type(exc))
