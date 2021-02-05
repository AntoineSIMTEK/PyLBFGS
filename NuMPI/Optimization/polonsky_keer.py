import numpy as np
import scipy.optimize as optim
import matplotlib as plt
from inspect import signature


def constrained_conjugate_gradients(objective, hessp, x0=None, gtol=1e-8,
                                    mean_value=None, residual_plot=False,
                                    maxiter=5000):
    """
    Implementation of constrained conjugate gradient algorithm as described in,
    I.A. Polonsky, L.M. Keer, Wear 231, 206 (1999).

    Parameters
    ----------
    objective : callable.
                The objective function to be minimized.
                            fun(x) -> float(energy),ndarray(gradient)
                where x is the input ndarray.
    hessp : callable
            Function to evaluate the hessian product of the objective.
            Hessp should accept either 1 argument (desscent direction) or
            2 arguments (x,descent direction).
                            hessp(des_dir)->ndarray
                                    or
                            hessp(x,des_dir)->ndarray
            where x is the input ndarray and des_dir is the descent direction.

    x0 : ndarray
         Initial guess. Default value->None.
         ValueError is raised if "None" is provided.

    gtol : float, optional
           Default value : 1e-8

    mean_value : int/float, optional
               If you want to apply the mean_value constraint then provide an
               int/float value to the mean_value.

    residual_plot : bool, optional
                    Generates a plot between the residual and iterations.

    maxiter : int,optional
              Default, maxiter=5000
              Maximum number of iterations after which the program will exit.

    Returns
    -------
    success : bool
              True if convergence else False.
    x : array
        array of minimized x.
    jac : array
          value of residual at convergence/non-convergence.
    nit : int
          Number of iterations
    message : string
              Convergence or Nodes_dir-Convergence

    References
    ----------
    ..[1] I.A. Polonsky, L.M. Keer, Wear 231, 206 (1999)
    """

    if not isinstance(mean_value, (type(None), int, float)):
        raise ValueError('Inappropriate type: {} for mean_value whereas a '
                         'float \
            or int is expected'.format(type(mean_value)))

    if not isinstance(residual_plot, bool):
        raise ValueError('Inappropriate type: {} for "residual_plot" whereas '
                         'a bool \
                         is expected'.format(type(residual_plot)))

    gtol = gtol
    fun = objective
    x0 = x0.flatten()
    if x0 is not None:
        x = x0.copy()
        # print("Total force is  :: {}".format(np.sum(x)))
        delta = 0
        G_old = 1
    else:
        raise ValueError('Input required for x0/initial value !!')

    grads = np.array([])
    iterations = np.array([])
    rms_pen_ = np.array([])

    des_dir = np.zeros(np.shape(x))

    if residual_plot:
        grads = np.append(grads, 0)
        iterations = np.append(iterations, 0)

    n_iterations = 1

    while (n_iterations < maxiter + 1):

        '''Mask to truncate the negative values'''
        mask_neg = x <= 0
        x[mask_neg] = 0.0

        '''Initial residual or GAP for polonsky-keer'''
        residual = fun(x)[1]

        mask_c = x > 0
        if mean_value is not None:
            residual = residual - np.mean(residual[mask_c])

        G = np.sum(residual[mask_c] ** 2)

        des_dir[mask_c] = -residual[mask_c] + delta * (G / G_old) * des_dir[
            mask_c]
        des_dir[np.logical_not(mask_c)] = 0
        G_old = G

        if mask_neg.sum() > 0:
            rms_pen = np.sqrt(G / mask_neg.sum())
        else:
            rms_pen = np.sqrt(G)

        '''Calculating alpha'''

        sig = signature(hessp)
        if len(sig.parameters) == 2:
            hessp_val = hessp(x, des_dir)
        elif len(sig.parameters) == 1:
            hessp_val = hessp(des_dir)
        else:
            raise ValueError('hessp function has to take max 1 arg (descent '
                             'dir) or 2 args (x, descent direction)')

        '''Here hessp_val is used as r_ij in original algorithm'''
        if mean_value is not None:
            hessp_val = hessp_val - np.mean(hessp_val[mask_c])

        '''alpha is TAU from algorithm'''
        if mask_c.sum() != 0:
            '''alpha is TAU from algorithm'''
            alpha = -np.sum(residual[mask_c] * des_dir[mask_c]) \
                / np.sum(hessp_val[mask_c] * des_dir[mask_c])
        else:
            alpha = 0.0

        if alpha < 0:
            print("it {} : hessian is negative along the descent direction. "
                  "You will probably need linesearch "
                  "or trust region".format(n_iterations))
        # assert alpha >= 0

        x[mask_c] += alpha * des_dir[mask_c]

        '''mask for contact'''
        mask_neg = x <= 0
        '''truncating negative values'''
        x[mask_neg] = 0.0

        mask_g = residual < 0
        mask_overlap = np.logical_and(mask_neg, mask_g)

        if mask_overlap.sum() == 0:
            delta = 1
        else:
            delta = 0
            x[mask_overlap] = x[mask_overlap] - alpha * residual[mask_overlap]

        if mean_value is not None:
            '''Take care of constraint a_x*a_y*sum(p_ij)=P0'''
            P = np.mean(x)
            P0 = mean_value
            x *= (P0 / P)

        if residual_plot:
            iterations = np.append(iterations, n_iterations)
            if mask_c.sum() != 0:
                grads = np.append(grads, np.max(abs(residual[mask_c])))
            else:
                grads = np.append(grads, np.max(abs(residual)))
            rms_pen_ = np.append(rms_pen_, rms_pen)

        n_iterations += 1
        res_convg = False
        assert np.logical_not(np.isnan(x).any())

        if n_iterations >= 3:
            '''If converged'''
            if mask_c.sum() != 0:
                if np.max(abs(residual[mask_c])) <= gtol:
                    res_convg = True
                else:
                    res_convg = False
            if (res_convg) and (rms_pen <= gtol):
                result = optim.OptimizeResult({'success': True,
                                               'x': x,
                                               'fun': rms_pen_,
                                               'jac': residual,
                                               'nit': n_iterations,
                                               'message': 'CONVERGENCE: '
                                                          'NORM_OF_GRADIENT_'
                                                          '<=_GTOL',
                                               })
                if residual_plot:
                    plt.pyplot.plot(iterations, np.log10(grads))
                    plt.pyplot.xlabel('iterations')
                    plt.pyplot.ylabel('residuals')
                    plt.pyplot.show()

                return result

            elif (n_iterations >= maxiter - 1):
                '''If no convergence'''
                result = optim.OptimizeResult({'success': False,
                                               'x': x,
                                               'fun': fun,
                                               'jac': residual,
                                               'nit': n_iterations,
                                               'message': 'NO-CONVERGENCE:',
                                               })

                if residual_plot:
                    plt.pyplot.plot(iterations, np.log10(grads))
                    plt.pyplot.xlabel('iterations')
                    plt.pyplot.ylabel('residuals')
                    plt.pyplot.show()
                    plt.pyplot.plot(range(n_iterations - 1),
                                    np.log10(rms_pen_))
                    plt.pyplot.xlabel('iterations')
                    plt.pyplot.ylabel('rms pen')
                    plt.pyplot.show()

                return result