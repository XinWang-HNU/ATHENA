from unittest import TestCase
import numpy as np
from athena.utils import (Normalizer, initialize_weights, linear_program_ineq,
                          local_linear_gradients, sort_eigpairs,
                          CrossValidation, rrmse, average_rrmse)
from athena.active import ActiveSubspaces
from athena.kas import KernelActiveSubspaces
from athena.feature_map import FeatureMap


class TestUtils(TestCase):
    def test_normalizer_init_lb(self):
        normalizer = Normalizer(np.arange(5), np.arange(2, 7))
        np.testing.assert_array_equal(normalizer.lb, np.arange(5))

    def test_normalizer_init_ub(self):
        normalizer = Normalizer(np.arange(5), np.arange(2, 7))
        np.testing.assert_array_equal(normalizer.ub, np.arange(2, 7))

    def test_normalizer_fit_transform(self):
        np.random.seed(42)
        normalizer = Normalizer(-2 * np.ones(3), 4 * np.ones(3))
        inputs = np.random.uniform(-2, 4, 12).reshape(4, 3)
        ref_inputs = normalizer.fit_transform(inputs)
        true_norm = np.array([[-0.25091976, 0.90142861, 0.46398788],
                              [0.19731697, -0.68796272, -0.68801096],
                              [-0.88383278, 0.73235229, 0.20223002],
                              [0.41614516, -0.95883101, 0.9398197]])
        np.testing.assert_array_almost_equal(true_norm, ref_inputs)

    def test_normalizer_inverse_transform(self):
        np.random.seed(42)
        normalizer = Normalizer(-2 * np.ones(3), 4 * np.ones(3))
        ref_inputs = np.array([-1, 0, 1])
        inputs = normalizer.inverse_transform(ref_inputs)
        true_unnorm = np.array([-2, 1, 4])
        np.testing.assert_array_equal(true_unnorm, inputs)

    def test_initialize_weights(self):
        matrix = np.random.uniform(-1, 1, 9).reshape(3, 3)
        weights = initialize_weights(matrix)
        true_weights = np.array([0.333333, 0.333333, 0.333333]).reshape(3, 1)
        np.testing.assert_array_almost_equal(true_weights, weights)

    def test_linear_program_ineq(self):
        c = np.ones((2, 1))
        A = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
        b = np.array([[0.1], [0.1], [0.1]])
        x = linear_program_ineq(c, A, b)
        true_x = np.array([0.1, 0.1]).reshape(2, 1)
        np.testing.assert_array_almost_equal(true_x, x)

    def test_local_linear_gradients_01(self):
        np.random.seed(42)
        inputs = np.random.uniform(-1.0, 1.0, size=(200, 2))
        outputs = 2 - 5 * inputs[:, 0] + 4 * inputs[:, 1]
        gradients = local_linear_gradients(inputs, outputs)[0]
        M = gradients.shape[0]
        np.testing.assert_array_almost_equal(gradients,
                                             np.tile(np.array([-5.0, 4.0]),
                                                     (M, 1)),
                                             decimal=9)

    def test_local_linear_gradients_02(self):
        np.random.seed(42)
        inputs = np.random.uniform(-1.0, 1.0, size=(200, 2))
        outputs = 2 - 5 * inputs[:, 0] + 4 * inputs[:, 1]
        gradients = local_linear_gradients(inputs, outputs, n_neighbors=8)[0]
        M = gradients.shape[0]
        np.testing.assert_array_almost_equal(gradients,
                                             np.tile(np.array([-5.0, 4.0]),
                                                     (M, 1)),
                                             decimal=9)

    def test_sort_eigpairs_evals(self):
        np.random.seed(42)
        matrix = np.random.uniform(-1, 1, 9).reshape(3, 3)
        evals = sort_eigpairs(matrix)[0]
        true_evals = np.array([[1.466942], [1.025235], [0.294945]])
        np.testing.assert_array_almost_equal(true_evals, evals)

    def test_sort_eigpairs_evects(self):
        np.random.seed(42)
        matrix = np.random.uniform(-1, 1, 9).reshape(3, 3)
        evects = sort_eigpairs(matrix)[1]
        true_evects = np.array([[0.511409, 0.515297, 0.687699],
                                [-0.653819, -0.286001, 0.700517],
                                [0.557657, -0.807881, 0.190647]])
        np.testing.assert_array_almost_equal(true_evects, evects)

    def test_cross_validation_01(self):
        cv = CrossValidation()
        self.assertIsNone(cv.inputs)

    def test_cross_validation_02(self):
        cv = CrossValidation()
        self.assertIsNone(cv.outputs)

    def test_cross_validation_03(self):
        cv = CrossValidation()
        self.assertIsNone(cv.gradients)

    def test_cross_validation_04(self):
        cv = CrossValidation()
        self.assertIsNone(cv.ss)

    def test_cross_validation_05(self):
        cv = CrossValidation()
        self.assertIsNone(cv.gp)

    def test_cross_validation_06(self):
        cv = CrossValidation()
        self.assertEqual(cv.gp_dimension, 1)

    def test_cross_validation_07(self):
        cv = CrossValidation()
        self.assertEqual(cv.folds, 5)

    def test_cross_validation_fit_01(self):
        np.random.seed(42)
        inputs = np.random.uniform(-1, 1, 15).reshape(5, -1)
        outputs = np.random.uniform(0, 5, 10).reshape(5, -1)
        gradients = np.random.uniform(-1, 1, 30).reshape(5, 2, 3)
        ss = ActiveSubspaces()
        csv = CrossValidation(inputs=inputs,
                              outputs=outputs,
                              gradients=gradients,
                              folds=3,
                              subspace=ss,
                              gp_dimension=2)
        csv.fit(inputs, gradients, outputs)
        self.assertEqual(csv.gp.X.shape[1], 2)

    def test_cross_validation_fit_02(self):
        np.random.seed(42)
        inputs = np.random.uniform(-1, 1, 15).reshape(5, -1)
        outputs = np.random.uniform(0, 5, 10).reshape(5, -1)
        gradients = np.random.uniform(-1, 1, 30).reshape(5, 2, 3)
        ss = ActiveSubspaces()
        csv = CrossValidation(inputs=inputs,
                              outputs=outputs,
                              gradients=gradients,
                              folds=3,
                              subspace=ss)
        csv.fit(inputs, gradients, outputs)
        self.assertIsNotNone(csv.gp)

    def test_cross_validation_run_01(self):
        np.random.seed(42)
        inputs = np.random.uniform(-1, 1, 15).reshape(5, -1)
        outputs = np.random.uniform(0, 5, 10).reshape(5, -1)
        gradients = np.random.uniform(-1, 1, 30).reshape(5, 2, 3)
        ss = ActiveSubspaces()
        csv = CrossValidation(inputs=inputs,
                              outputs=outputs,
                              gradients=gradients,
                              folds=2,
                              subspace=ss)
        true_value = (8.186941403385733, 6.081926389368339)
        np.testing.assert_array_almost_equal(csv.run(), true_value)

    def test_cross_validation_run_02(self):
        np.random.seed(42)
        inputs = np.random.uniform(-1, 1, 10).reshape(5, 2)
        outputs = np.random.uniform(0, 5, 10).reshape(5, 2)
        gradients = np.random.uniform(-1, 1, 20).reshape(5, 2, 2)
        fm = FeatureMap(distr='laplace',
                        bias=np.random.uniform(-1, 1, 3),
                        input_dim=2,
                        n_features=3,
                        params=np.zeros(1),
                        sigma_f=outputs.var())
        ss = KernelActiveSubspaces(feature_map=fm)
        csv = CrossValidation(inputs=inputs,
                              outputs=outputs,
                              gradients=gradients,
                              folds=2,
                              subspace=ss)
        true_value = (2.26333743325053, 0.43902733603381605)
        np.testing.assert_array_almost_equal(csv.run(), true_value)

    def test_rrmse_01(self):
        np.random.seed(42)
        predictions = np.random.uniform(-1, 1, 5).reshape(5)
        targets = np.random.uniform(-1, 1, 5).reshape(5)
        true = 1.5298111757191089
        np.testing.assert_array_equal(rrmse(predictions, targets), true)

    def test_rrmse_02(self):
        np.random.seed(42)
        predictions = np.random.uniform(-1, 1, 10).reshape(5, 2)
        targets = np.random.uniform(-1, 1, 10).reshape(5, 2)
        true = 0.9089760363050161
        np.testing.assert_array_equal(rrmse(predictions, targets), true)

    def test_average_rrmse_01(self):
        np.random.seed(42)
        inputs = np.random.uniform(-1, 1, 10).reshape(5, 2)
        outputs = np.random.uniform(0, 5, 10).reshape(5, 2)
        gradients = np.random.uniform(-1, 1, 20).reshape(5, 2, 2)
        fm = FeatureMap(distr='laplace',
                        bias=np.random.uniform(-1, 1, 3),
                        input_dim=2,
                        n_features=3,
                        params=np.zeros(1),
                        sigma_f=outputs.var())
        ss = KernelActiveSubspaces(feature_map=fm)
        csv = CrossValidation(inputs=inputs,
                              outputs=outputs,
                              gradients=gradients,
                              folds=2,
                              subspace=ss)
        best = [0.1, np.zeros((3, 2))]
        hyperparams = np.array([-1.])
        score = average_rrmse(hyperparams, csv, best, resample=1)
        np.testing.assert_equal(best[0], 0.1)

    def test_average_rrmse_02(self):
        np.random.seed(42)
        inputs = np.random.uniform(-1, 1, 10).reshape(5, 2)
        outputs = np.random.uniform(0, 5, 10).reshape(5, 2)
        gradients = np.random.uniform(-1, 1, 20).reshape(5, 2, 2)
        fm = FeatureMap(distr='laplace',
                        bias=np.random.uniform(-1, 1, 3),
                        input_dim=2,
                        n_features=3,
                        params=np.zeros(1),
                        sigma_f=outputs.var())
        ss = KernelActiveSubspaces(feature_map=fm)
        csv = CrossValidation(inputs=inputs,
                              outputs=outputs,
                              gradients=gradients,
                              folds=2,
                              subspace=ss)
        best = [0.1, np.zeros((3, 2))]
        hyperparams = np.array([-1.])
        score = average_rrmse(hyperparams, csv, best, resample=1)
        true = 2.135718555831271
        np.testing.assert_equal(score, true)
