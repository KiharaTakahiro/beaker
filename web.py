from common.beaker import BeakerRouter
router = BeakerRouter()

from controllers.welcome_controller import welcome, welcome_post, welcome_get_csv

router.get('/', welcome)
router.get('/get_csv', welcome_get_csv)
router.post('/welcome_post', welcome_post)