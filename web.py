from common.beaker import BeakerRouter
router = BeakerRouter()

from controllers.welcome_controller import welcome

router.get('/', welcome)