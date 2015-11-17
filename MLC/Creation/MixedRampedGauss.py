from BaseCreation import BaseCreation
import numpy as np

class MixedRampedGauss(BaseCreation):
    def create(self, eng, config):
        ramp = np.fromstring(config.get('GP', 'ramp'), dtype=int, sep=',')
        center = (np.max(ramp) + np.amin(ramp)) / 2
        sigma = config.get('GP', 'sigma')

        # normalization =
        # (ramp - center) ** 2



"""
            changed_param=mlc_parameters;
            minde=min(mlc_parameters.ramp);
            maxde=max(mlc_parameters.ramp);
            center=round((maxde+minde)/2);
            r=mlc_parameters.ramp;
            sigma=mlc_parameters.gaussigma;
            g=(exp(-((r-center).^2)/sigma^2)/sum(exp(-((r-center).^2)/sigma^2)))*n_indiv_to_generate;
            n=[0 round(cumsum(g))];
            for j=1:length(n)-1;
                changed_param.maxdepthfirst=mlc_parameters.ramp(j);
                [mlcpop,mlctable,i]=fill_creation(mlcpop,mlctable,changed_param,indiv_to_generate(1:n(j)+round((n(j+1)-n(j))/2)),i,1,verb);
                [mlcpop,mlctable,i]=fill_creation(mlcpop,mlctable,changed_param,indiv_to_generate(1:n(j+1)),i,3,verb);
            end
"""
