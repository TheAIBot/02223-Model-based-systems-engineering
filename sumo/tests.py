import unittest
import simulator as sim
import trafficLightControllers.staticLights as staticLightCtrl
import trafficLightControllers.dynamicTrafficLights as dynamicLightCtrl

class TestSmallMaps(unittest.TestCase):

    def test_single_cross_light(self):
        staticSim = sim.SumoSim("path to map file", staticLightCtrl.staticTrafficLightController())
        staticTime = staticSim.run()

        dynamicSim = sim.SumoSim("path to map file", dynamicLightCtrl.dynamicTrafficLightController())
        dynamicTime = dynamicSim.run()

        self.assertTrue(staticTime > dynamicTime)

    def test_single_t_light(self):
        pass

    def test_cross_and_t_light(self):
        pass

    def test_dual_t_light(self):
        pass

    def test_dual_cross_light(self):
        pass

    def test_quad_cross_light(self):
        pass





if __name__ == '__main__':
    unittest.main()