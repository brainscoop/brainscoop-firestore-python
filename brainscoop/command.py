import data
import helper
import logging
import os


def _is_collection_path(path):
    return len(path.split('/')) == 1


def bootstrap(db, opts):
    batch = db.batch()
    for _ in range(0, opts.num):
        d = data.generate(os.path.join(opts.schema, 'user-schema.json'))
        user_id = helper.id_from_name(d.get('first'), d.get('last'))
        user_ref = db.document('users/{}'.format(user_id))
        batch.set(user_ref, d)
        logging.info('Adding doc "users/{}".'.format(user_ref.id))
    batch.commit()


def delete(db, opts):
    if _is_collection_path(opts.path):
        delete_collection(db.collection(opts.path), 10)
    else:
        db.document(opts.path).delete()
        logging.info('Deleting doc "{}".'.format(opts.path))


def delete_collection(coll_ref, batch_size):
    docs = coll_ref.limit(10).get()
    deleted = 0

    for doc in docs:
        doc.reference.delete()
        deleted = deleted + 1
        logging.info('Deleting doc "{}/{}".'.format(coll_ref.id, doc.id))

    if deleted >= batch_size:
        delete_collection(coll_ref, batch_size)


def dump(db, opts):
    if _is_collection_path(opts.path):
        dump_collection(db.collection(opts.path))
    else:
        doc = db.document(opts.path).get()
        print('{} => {}'.format(doc.id, doc.to_dict()))


def dump_collection(coll_ref):
    docs = coll_ref.get()
    for doc in docs:
        print('{} => {}'.format(doc.id, doc.to_dict()))


def update(db, opts):
    doc_ref = db.document(opts.path)
    doc_ref.update(helper.dict_from_kv_opt(opts.field))
    logging.info('Updating doc "{}" => {}.'.format(doc_ref.id, opts.field))
