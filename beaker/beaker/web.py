from common.beaker import BeakerRouter
router = BeakerRouter()

from controllers.welcome_controller import welcome, welcome_post, welcome_get_csv, welcome_db, welcome_error_test

router.get('/', welcome)
router.get('/get_csv', welcome_get_csv)
router.get('/error_test', welcome_error_test)
router.get('/welcome_db', welcome_db)
router.post('/welcome_post', welcome_post)