
import numpy as np
from magal.photometry.syntphot import spec2filter
from astropy.io import fits


# Criando a curva de transmissao do filtro


yc = 4003 # lambda central em Angstroms
dy = 141 # delta lambda em Angstroms
res = 0.5 # resolucao espectral da curva de transmissao em Angstroms

# gera curva de transmissao teorica
wl = np.arange(yc-dy,yc+dy,res)
transm = np.zeros(len(wl))
mask = np.bitwise_and(wl > yc-dy/2., wl < yc+dy/2.)
transm[mask] = 1.0

# curva de transmissao a ser salva em arquivos do tipo .npy com a funcao np.save()
jpas4000 = np.array( zip( wl, transm), dtype = [ ('wl', np.float) , ('transm', np.float) ])

# np.save('jpas4000.npy',jpas4000)

# Abre arquivo fits com o espectro modelo.
hdu = fits.open('/Volumes/TiagoHD2/Documents/template/s_coelho14_sed/t06250_g+4.5_m05p00_sed.fits')

# Mudar para o caso de espectros full res!
wl = 10.**(hdu[0].header['CRVAL1']+np.arange(0,len(hdu[0].data))*hdu[0].header['CD1_1'])

obs_spec = np.array( zip(wl, hdu[0].data) , dtype = [('wl',np.float), ('flux',np.float)])

# usa funcao spec2filter para calcular magnitude absoluta na banda
print spec2filter(jpas4000,obs_spec)