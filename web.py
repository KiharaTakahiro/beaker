from common.beaker import BeakerRouter
router = BeakerRouter()

from controllers.welcome_controller import welcome, welcome_post

router.get('/', welcome)
router.post('/welcome_post', welcome_post)