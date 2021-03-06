import sys
import os
import numpy as np
from numpy.random import choice, randn, uniform
from tools.config import conf, load_config
import pandas as pd

class dev_PARMAN:

    def __init__(self):
        self.get_ordered_free_params()
        self.set_new_params(self.par, initial=True)

    def get_ordered_free_params(self):
        self.par = []
        self.order = []

        for k in conf['params']:
            for kk in conf['params'][k]:
                if conf['params'][k][kk]['fixed'] == False:
                    # p=uniform(conf['params'][k][kk]['min'],conf['params'][k][kk]['max'],1)[0]
                    self.par.append(conf['params'][k][kk]['value'])
                    self.order.append([1, k, kk])

        if 'datasets' in conf:
            for k in conf['datasets']:
                for kk in conf['datasets'][k]['norm']:
                    if conf['datasets'][k]['norm'][kk]['fixed'] == False:
                        self.par.append(conf['datasets'][k]
                                        ['norm'][kk]['value'])
                        self.order.append([2, k, kk])

    def set_new_params(self, parnew, initial=False):
        self.shifts = 0
        semaphore = {}

        for i in range(len(self.order)):
            ii, k, kk = self.order[i]
            if ii == 1:
                if k not in semaphore:
                    semaphore[k] = 0
                if conf['params'][k][kk]['value'] != parnew[i]:
                    conf['params'][k][kk]['value'] = parnew[i]
                    semaphore[k] = 1
                    self.shifts += 1
            elif ii == 2:
                if conf['datasets'][k]['norm'][kk]['value'] != parnew[i]:
                    conf['datasets'][k]['norm'][kk]['value'] = parnew[i]
                    self.shifts += 1

        if initial:
            for k in conf['params']:
                semaphore[k] = 1

        if semaphore['pdf']==1: semaphore['pdfpi-']=1 #This is needed so the pion widths get updated when they are set equal to the proton widths

        self.propagate_params(semaphore)

    def gen_report(self):
        """
        Get a report.

        Returns:
            A list of the lines of the report.
        """
        L = []

        for k in conf['params']:
            for kk in sorted(conf['params'][k]):
                if conf['params'][k][kk]['fixed'] == False:
                    if conf['params'][k][kk]['value'] < 0:
                        L.append('%-10s  %-20s  %10.5e' %
                                 (k, kk, conf['params'][k][kk]['value']))
                    else:
                        L.append('%-10s  %-20s   %10.5e' %
                                 (k, kk, conf['params'][k][kk]['value']))

        for k in conf['datasets']:
            for kk in conf['datasets'][k]['norm']:
                if conf['datasets'][k]['norm'][kk]['fixed'] == False:
                    L.append('%10s %10s %10d  %10.5e' % (
                        'norm', k, kk, conf['datasets'][k]['norm'][kk]['value']))
        return L

    def propagate_params(self, semaphore):
        if 'pdf'          in semaphore and semaphore['pdf']          == 1: self.set_pdf_params()
        if 'pdfpi-'       in semaphore and semaphore['pdfpi-']       == 1: self.set_pdfpi_params()
        if 'transversity' in semaphore and semaphore['transversity'] == 1: self.set_transversity_params()
        if 'sivers'       in semaphore and semaphore['sivers']       == 1: self.set_sivers_params()
        if 'boermulders'  in semaphore and semaphore['boermulders']  == 1: self.set_boermulders_params()
        if 'ffpi'         in semaphore and semaphore['ffpi']         == 1: self.set_ffpi_params()
        if 'ffk'          in semaphore and semaphore['ffk']          == 1: self.set_ffk_params()
        if 'collinspi'    in semaphore and semaphore['collinspi']    == 1: self.set_collinspi_params()
        if 'collinsk'     in semaphore and semaphore['collinsk']     == 1: self.set_collinsk_params()
        if 'Htildepi'    in semaphore and semaphore['Htildepi']    == 1: self.set_Htildepi_params()
        if 'Htildek'     in semaphore and semaphore['Htildek']     == 1: self.set_Htildek_params()

    def set_constraits(self, parkind):

        for k in conf['params'][parkind]:
            if conf['params'][parkind][k]['fixed'] == True:  continue
            elif conf['params'][parkind][k]['fixed'] == False: continue
            elif 'proton widths uv' in conf['params'][parkind][k]['fixed']:
                conf['params'][parkind][k]['value'] = conf['params']['pdf']['widths1_uv']['value']
            elif 'proton widths sea' in conf['params'][parkind][k]['fixed']:
                conf['params'][parkind][k]['value'] = conf['params']['pdf']['widths1_sea']['value']
            else:
                ref_par = conf['params'][parkind][k]['fixed']
                conf['params'][parkind][k]['value'] = conf['params'][parkind][ref_par]['value']
        
    def set_pdf_params(self):
        self.set_constraits('pdf')
        hadron='p'
        conf['pdf']._widths1_uv  = conf['params']['pdf']['widths1_uv' ]['value']
        conf['pdf']._widths1_dv  = conf['params']['pdf']['widths1_dv' ]['value']
        conf['pdf']._widths1_sea = conf['params']['pdf']['widths1_sea']['value']
        conf['pdf']._widths2_uv  = conf['params']['pdf']['widths2_uv' ]['value']
        conf['pdf']._widths2_dv  = conf['params']['pdf']['widths2_dv' ]['value']
        conf['pdf']._widths2_sea = conf['params']['pdf']['widths2_sea']['value']
        conf['pdf'].setup(hadron)

    def set_pdfpi_params(self):
        self.set_constraits('pdfpi-')
        hadron='pi-'
        conf['pdfpi-']._widths1_ubv = conf['params']['pdfpi-']['widths1_ubv' ]['value']
        conf['pdfpi-']._widths1_dv  = conf['params']['pdfpi-']['widths1_dv' ]['value']
        conf['pdfpi-']._widths1_sea = conf['params']['pdfpi-']['widths1_sea']['value']
        conf['pdfpi-']._widths2_ubv = conf['params']['pdfpi-']['widths2_ubv' ]['value']
        conf['pdfpi-']._widths2_dv  = conf['params']['pdfpi-']['widths2_dv' ]['value']
        conf['pdfpi-']._widths2_sea = conf['params']['pdfpi-']['widths2_sea']['value']       
        conf['pdfpi-'].setup(hadron)

    def set_transversity_params(self):
        self.set_constraits('transversity')

        conf['transversity']._widths1_uv  = conf['params']['transversity']['widths1_uv']['value']
        conf['transversity']._widths1_dv  = conf['params']['transversity']['widths1_dv']['value']
        conf['transversity']._widths1_sea = conf['params']['transversity']['widths1_sea']['value']

        conf['transversity']._widths2_uv  = conf['params']['transversity']['widths2_uv']['value']
        conf['transversity']._widths2_dv  = conf['params']['transversity']['widths2_dv']['value']
        conf['transversity']._widths2_sea = conf['params']['transversity']['widths2_sea']['value']

        iflav=0
        for flav in ['u','ub','d','db','s','sb']:
            iflav+=1
            ipar=-1
            for par in ['N0','a0','b0','c0','d0','N1','a1','b1','c1','d1']:
                ipar+=1
                if '%s %s 1'%(flav,par) in conf['params']['transversity']:
                    conf['transversity'].shape1[iflav][ipar] = conf['params']['transversity']['%s %s 1'%(flav,par)]['value']
                if '%s %s 2'%(flav,par) in conf['params']['transversity']:
                    conf['transversity'].shape2[iflav][ipar] = conf['params']['transversity']['%s %s 2'%(flav,par)]['value']

        conf['transversity'].setup()

    def set_sivers_params(self):
        self.set_constraits('sivers')

        conf['sivers']._widths1_uv  = conf['params']['sivers']['widths1_uv']['value']
        conf['sivers']._widths1_dv  = conf['params']['sivers']['widths1_dv']['value']
        conf['sivers']._widths1_sea = conf['params']['sivers']['widths1_sea']['value']

        conf['sivers']._widths2_uv  = conf['params']['sivers']['widths2_uv']['value']
        conf['sivers']._widths2_dv  = conf['params']['sivers']['widths2_dv']['value']
        conf['sivers']._widths2_sea = conf['params']['sivers']['widths2_sea']['value']

        iflav=0
        for flav in ['u','ub','d','db','s','sb']:
            iflav+=1
            ipar=-1
            for par in ['N0','a0','b0','c0','d0','N1','a1','b1','c1','d1']:
                ipar+=1
                if '%s %s 1'%(flav,par) in conf['params']['sivers']:
                    conf['sivers'].shape1[iflav][ipar] = conf['params']['sivers']['%s %s 1'%(flav,par)]['value']
                if '%s %s 2'%(flav,par) in conf['params']['sivers']:
                    conf['sivers'].shape2[iflav][ipar] = conf['params']['sivers']['%s %s 2'%(flav,par)]['value']

        conf['sivers'].setup()

    def set_boermulders_params(self):
        self.set_constraits('boermulders')

        conf['boermulders']._widths1_uv  = conf['params']['boermulders']['widths1_uv']['value']
        conf['boermulders']._widths1_dv  = conf['params']['boermulders']['widths1_dv']['value']
        conf['boermulders']._widths1_sea = conf['params']['boermulders']['widths1_sea']['value']

        conf['boermulders']._widths2_uv  = conf['params']['boermulders']['widths2_uv']['value']
        conf['boermulders']._widths2_dv  = conf['params']['boermulders']['widths2_dv']['value']
        conf['boermulders']._widths2_sea = conf['params']['boermulders']['widths2_sea']['value']

        iflav=0
        for flav in ['u','ub','d','db','s','sb']:
            iflav+=1
            ipar=-1
            for par in ['N0','a0','b0','c0','d0','N1','a1','b1','c1','d1']:
                ipar+=1
                if '%s %s 1'%(flav,par) in conf['params']['boermulders']:
                    conf['boermulders'].shape1[iflav][ipar] = conf['params']['boermulders']['%s %s 1'%(flav,par)]['value']
                if '%s %s 2'%(flav,par) in conf['params']['boermulders']:
                    conf['boermulders'].shape2[iflav][ipar] = conf['params']['boermulders']['%s %s 2'%(flav,par)]['value']

        conf['boermulders'].setup()

    def set_ffpi_params(self):
        self.set_constraits('ffpi')
        conf['ffpi']._widths1_fav  = conf['params']['ffpi']['widths1_fav']['value']
        conf['ffpi']._widths1_ufav = conf['params']['ffpi']['widths1_ufav']['value']
        conf['ffpi']._widths2_fav  = conf['params']['ffpi']['widths2_fav']['value']
        conf['ffpi']._widths2_ufav = conf['params']['ffpi']['widths2_ufav']['value']
        conf['ffpi'].setup()

    def set_ffk_params(self):
        self.set_constraits('ffk')
        conf['ffk']._widths1_fav   = conf['params']['ffk']['widths1_fav']['value']
        conf['ffk']._widths1_ufav  = conf['params']['ffk']['widths1_ufav']['value']
        conf['ffk']._widths2_fav   = conf['params']['ffk']['widths2_fav']['value']
        conf['ffk']._widths2_ufav  = conf['params']['ffk']['widths2_ufav']['value']
        conf['ffk'].setup()

    def set_collinspi_params(self):
        self.set_constraits('collinspi')
        conf['collinspi']._widths1_fav  = conf['params']['collinspi']['widths1_fav']['value']
        conf['collinspi']._widths1_ufav = conf['params']['collinspi']['widths1_ufav']['value']
        conf['collinspi']._widths2_fav  = conf['params']['collinspi']['widths2_fav']['value']
        conf['collinspi']._widths2_ufav = conf['params']['collinspi']['widths2_ufav']['value']

        iflav=0
        for flav in ['u','ub','d','db','s','sb']:
            iflav+=1
            ipar=-1
            for par in ['N0','a0','b0','c0','d0','N1','a1','b1','c1','d1']:
                ipar+=1
                if '%s %s 1'%(flav,par) in conf['params']['collinspi']:
                    conf['collinspi'].shape1[iflav][ipar] = conf['params']['collinspi']['%s %s 1'%(flav,par)]['value']
                if '%s %s 2'%(flav,par) in conf['params']['collinspi']:
                    conf['collinspi'].shape2[iflav][ipar] = conf['params']['collinspi']['%s %s 2'%(flav,par)]['value']
        conf['collinspi'].setup()

    def set_collinsk_params(self):
        self.set_constraits('collinsk')
        conf['collinsk']._widths1_fav   = conf['params']['collinsk']['widths1_fav']['value']
        conf['collinsk']._widths1_ufav  = conf['params']['collinsk']['widths1_ufav']['value']
        conf['collinsk']._widths2_fav   = conf['params']['collinsk']['widths2_fav']['value']
        conf['collinsk']._widths2_ufav  = conf['params']['collinsk']['widths2_ufav']['value']
        iflav=0
        for flav in ['u','ub','d','db','s','sb']:
            iflav+=1
            ipar=-1
            for par in ['N0','a0','b0','c0','d0','N1','a1','b1','c1','d1']:
                ipar+=1
                if '%s %s 1'%(flav,par) in conf['params']['collinsk']:
                    conf['collinsk'].shape1[iflav][ipar] = conf['params']['collinsk']['%s %s 1'%(flav,par)]['value']
                if '%s %s 2'%(flav,par) in conf['params']['collinsk']:
                    conf['collinsk'].shape2[iflav][ipar] = conf['params']['collinsk']['%s %s 2'%(flav,par)]['value']
        conf['collinsk'].setup()

    def set_Htildepi_params(self):
            self.set_constraits('Htildepi')
            conf['Htildepi']._widths1_fav  = conf['params']['Htildepi']['widths1_fav']['value']
            conf['Htildepi']._widths1_ufav = conf['params']['Htildepi']['widths1_ufav']['value']
            conf['Htildepi']._widths2_fav  = conf['params']['Htildepi']['widths2_fav']['value']
            conf['Htildepi']._widths2_ufav = conf['params']['Htildepi']['widths2_ufav']['value']

            iflav=0
            for flav in ['u','ub','d','db','s','sb']:
                iflav+=1
                ipar=-1
                for par in ['N0','a0','b0','c0','d0','N1','a1','b1','c1','d1']:
                    ipar+=1
                    if '%s %s 1'%(flav,par) in conf['params']['Htildepi']:
                        conf['Htildepi'].shape1[iflav][ipar] = conf['params']['Htildepi']['%s %s 1'%(flav,par)]['value']
                    if '%s %s 2'%(flav,par) in conf['params']['Htildepi']:
                        conf['Htildepi'].shape2[iflav][ipar] = conf['params']['Htildepi']['%s %s 2'%(flav,par)]['value']
            conf['Htildepi'].setup()

    def set_Htildek_params(self):
            self.set_constraits('Htildek')
            conf['Htildek']._widths1_fav   = conf['params']['Htildek']['widths1_fav']['value']
            conf['Htildek']._widths1_ufav  = conf['params']['Htildek']['widths1_ufav']['value']
            conf['Htildek']._widths2_fav   = conf['params']['Htildek']['widths2_fav']['value']
            conf['Htildek']._widths2_ufav  = conf['params']['Htildek']['widths2_ufav']['value']
            iflav=0
            for flav in ['u','ub','d','db','s','sb']:
                iflav+=1
                ipar=-1
                for par in ['N0','a0','b0','c0','d0','N1','a1','b1','c1','d1']:
                    ipar+=1
                    if '%s %s 1'%(flav,par) in conf['params']['Htildek']:
                        conf['Htildek'].shape1[iflav][ipar] = conf['params']['Htildek']['%s %s 1'%(flav,par)]['value']
                    if '%s %s 2'%(flav,par) in conf['params']['Htildek']:
                        conf['Htildek'].shape2[iflav][ipar] = conf['params']['Htildek']['%s %s 2'%(flav,par)]['value']
            conf['Htildek'].setup()

class PARMAN:

    def __init__(self):
        self.get_ordered_free_params()
  
    def get_ordered_free_params(self):
        self.par=[]
        self.order=[]
        self.pmin=[]
        self.pmax=[]
     
        if 'check lims' not in conf: conf['check lims']=False
  
        for k in conf['params']:
            for kk in conf['params'][k]:
                if  conf['params'][k][kk]['fixed']==False:
                    p=conf['params'][k][kk]['value']
                    pmin=conf['params'][k][kk]['min']
                    pmax=conf['params'][k][kk]['max']
                    self.pmin.append(pmin)
                    self.pmax.append(pmax)
                    if p<pmin or p>pmax: 
                       if conf['check lims']: raise ValueError('par limits are not consistend with central: %s %s'%(k,kk))
  
                    self.par.append(p)
                    self.order.append([1,k,kk])
  
        if 'datasets' in conf:
            for k in conf['datasets']:
                for kk in conf['datasets'][k]['norm']:
                    if  conf['datasets'][k]['norm'][kk]['fixed']==False:
                        p=conf['datasets'][k]['norm'][kk]['value']
                        pmin=conf['datasets'][k]['norm'][kk]['min']
                        pmax=conf['datasets'][k]['norm'][kk]['max']
                        self.pmin.append(pmin)
                        self.pmax.append(pmax)
                        if p<pmin or p>pmax: 
                           if conf['check lims']: raise ValueError('par limits are not consistend with central: %s %s'%(k,kk))
                        self.par.append(p)
                        self.order.append([2,k,kk])
  
        self.pmin=np.array(self.pmin)
        self.pmax=np.array(self.pmax)
        self.par=np.array(self.par)
        self.set_new_params(self.par,initial=True)
  
    def gen_flat(self,setup=True):
        r=uniform(0,1,len(self.par))
        par=self.pmin + r * (self.pmax-self.pmin)
        if setup: self.set_new_params(par,initial=True)        
        return par
        #while 1:
        #  r=uniform(0,1,len(self.par))
        #  par=self.pmin + r * (self.pmax-self.pmin)
        #  self.set_new_params(par,initial=True)        
        #  flag=False
        #  if 'pdf' in conf and conf['pdf'].params['g1'][0]<0: flag=True
        #  if 'pdf' in conf and conf['pdf'].params['s1'][0]<0: flag=True
        #  if flag==False: break
        #return par
  
    def check_lims(self):
        flag=True    
        for k in conf['params']:
            for kk in conf['params'][k]:
                if  conf['params'][k][kk]['fixed']==False:
                    p=conf['params'][k][kk]['value']
                    pmin=conf['params'][k][kk]['min']
                    pmax=conf['params'][k][kk]['max']
                    if  p<pmin or p>pmax: 
                        print k,kk, p,pmin,pmax
                        flag=False
  
        if  'datasets' in conf:
            for k in conf['datasets']:
                for kk in conf['datasets'][k]['norm']:
                    if  conf['datasets'][k]['norm'][kk]['fixed']==False:
                        p=conf['datasets'][k]['norm'][kk]['value']
                        pmin=conf['datasets'][k]['norm'][kk]['min']
                        pmax=conf['datasets'][k]['norm'][kk]['max']
                        if p<pmin or p>pmax:
                          flag=False
                          print k,kk, p,pmin,pmax
  
        return flag
  
    def set_new_params(self,parnew,initial=False):
        self.par=parnew
        self.shifts=0
        semaphore={}
  
        for i in range(len(self.order)):
            ii,k,kk=self.order[i]  
            if  ii==1:
                if k not in semaphore: semaphore[k]=0
                if conf['params'][k][kk]['value']!=parnew[i]:
                  conf['params'][k][kk]['value']=parnew[i]
                  semaphore[k]=1
                  self.shifts+=1
            elif ii==2:
                if conf['datasets'][k]['norm'][kk]['value']!=parnew[i]:
                  conf['datasets'][k]['norm'][kk]['value']=parnew[i]
                  self.shifts+=1
  
        if  initial:
            for k in conf['params']: semaphore[k]=1
        
        #--This is needed so the pion widths get updated 
        #--when they are set equal to the proton widths
        if semaphore['pdf']==1 and 'pdfp1-' in conf['params']: semaphore['pdfpi-']=1 
  
        self.propagate_params(semaphore)
  
    def gen_report(self):
        L=[]
        cnt=0
        for k in conf['params']:
            for kk in sorted(conf['params'][k]):
                if  conf['params'][k][kk]['fixed']==False: 
                    cnt+=1
                    if  conf['params'][k][kk]['value']<0:
                        L.append('%d %10s  %10s  %10.5e'%(cnt,k,kk,conf['params'][k][kk]['value']))
                    else:
                        L.append('%d %10s  %10s   %10.5e'%(cnt,k,kk,conf['params'][k][kk]['value']))
  
        for k in conf['datasets']:
            for kk in conf['datasets'][k]['norm']:
                if  conf['datasets'][k]['norm'][kk]['fixed']==False: 
                    cnt+=1
                    L.append('%d %10s %10s %10d  %10.5e'%(cnt,'norm',k,kk,conf['datasets'][k]['norm'][kk]['value']))
        return L
 
    def propagate_params(self,semaphore):
      flag=False
      if 'pdf'          in semaphore and semaphore['pdf']          == 1: self.set_pdf_params()
      if 'pdfpi-'       in semaphore and semaphore['pdfpi-']       == 1: self.set_pdfpi_params()
      if 'transversity' in semaphore and semaphore['transversity'] == 1: self.set_transversity_params()
      if 'sivers'       in semaphore and semaphore['sivers']       == 1: self.set_sivers_params()
      if 'boermulders'  in semaphore and semaphore['boermulders']  == 1: self.set_boermulders_params()
      if 'ffpi'         in semaphore and semaphore['ffpi']         == 1: self.set_ffpi_params()
      if 'ffk'          in semaphore and semaphore['ffk']          == 1: self.set_ffk_params()
      if 'collinspi'    in semaphore and semaphore['collinspi']    == 1: self.set_collinspi_params()
      if 'collinsk'     in semaphore and semaphore['collinsk']     == 1: self.set_collinsk_params()
      if 'Htildepi'     in semaphore and semaphore['Htildepi']     == 1: self.set_Htildepi_params()
      if 'Htildek'      in semaphore and semaphore['Htildek']      == 1: self.set_Htildek_params()

    def set_constraits(self, parkind):

        for k in conf['params'][parkind]:
            if conf['params'][parkind][k]['fixed'] == True:  continue
            elif conf['params'][parkind][k]['fixed'] == False: continue
            elif 'proton widths uv' in conf['params'][parkind][k]['fixed']: 
                conf['params'][parkind][k]['value'] = conf['params']['pdf']['widths1_uv']['value']
            elif 'proton widths sea' in conf['params'][parkind][k]['fixed']:
                conf['params'][parkind][k]['value'] = conf['params']['pdf']['widths1_sea']['value']
            else:
                ref_par = conf['params'][parkind][k]['fixed']
                conf['params'][parkind][k]['value'] = conf['params'][parkind][ref_par]['value']

    def set_pdf_params(self):
        self.set_constraits('pdf')
        hadron='p'
        conf['pdf']._widths1_uv  = conf['params']['pdf']['widths1_uv' ]['value']
        conf['pdf']._widths1_dv  = conf['params']['pdf']['widths1_dv' ]['value']
        conf['pdf']._widths1_sea = conf['params']['pdf']['widths1_sea']['value']
        conf['pdf']._widths2_uv  = conf['params']['pdf']['widths2_uv' ]['value']
        conf['pdf']._widths2_dv  = conf['params']['pdf']['widths2_dv' ]['value']
        conf['pdf']._widths2_sea = conf['params']['pdf']['widths2_sea']['value']
        conf['pdf'].setup(hadron)

    def set_pdfpi_params(self):
        self.set_constraits('pdfpi-')
        hadron='pi-'
        conf['pdfpi-']._widths1_ubv = conf['params']['pdfpi-']['widths1_ubv' ]['value']
        conf['pdfpi-']._widths1_dv  = conf['params']['pdfpi-']['widths1_dv' ]['value']
        conf['pdfpi-']._widths1_sea = conf['params']['pdfpi-']['widths1_sea']['value']
        conf['pdfpi-']._widths2_ubv = conf['params']['pdfpi-']['widths2_ubv' ]['value']
        conf['pdfpi-']._widths2_dv  = conf['params']['pdfpi-']['widths2_dv' ]['value']
        conf['pdfpi-']._widths2_sea = conf['params']['pdfpi-']['widths2_sea']['value']
        conf['pdfpi-'].setup(hadron)

    def set_transversity_params(self):
        self.set_constraits('transversity')

        conf['transversity']._widths1_uv  = conf['params']['transversity']['widths1_uv']['value']
        conf['transversity']._widths1_dv  = conf['params']['transversity']['widths1_dv']['value']
        conf['transversity']._widths1_sea = conf['params']['transversity']['widths1_sea']['value']

        conf['transversity']._widths2_uv  = conf['params']['transversity']['widths2_uv']['value']
        conf['transversity']._widths2_dv  = conf['params']['transversity']['widths2_dv']['value']
        conf['transversity']._widths2_sea = conf['params']['transversity']['widths2_sea']['value']

        iflav=0
        for flav in ['u','ub','d','db','s','sb']:
            iflav+=1
            ipar=-1
            for par in ['N0','a0','b0','c0','d0','N1','a1','b1','c1','d1']:
                ipar+=1
                if '%s %s 1'%(flav,par) in conf['params']['transversity']:
                    conf['transversity'].shape1[iflav][ipar] = conf['params']['transversity']['%s %s 1'%(flav,par)]['value']
                if '%s %s 2'%(flav,par) in conf['params']['transversity']:
                    conf['transversity'].shape2[iflav][ipar] = conf['params']['transversity']['%s %s 2'%(flav,par)]['value']

        conf['transversity'].setup()

    def set_sivers_params(self):
        self.set_constraits('sivers')

        conf['sivers']._widths1_uv  = conf['params']['sivers']['widths1_uv']['value']
        conf['sivers']._widths1_dv  = conf['params']['sivers']['widths1_dv']['value']
        conf['sivers']._widths1_sea = conf['params']['sivers']['widths1_sea']['value']

        conf['sivers']._widths2_uv  = conf['params']['sivers']['widths2_uv']['value']
        conf['sivers']._widths2_dv  = conf['params']['sivers']['widths2_dv']['value']
        conf['sivers']._widths2_sea = conf['params']['sivers']['widths2_sea']['value']

        iflav=0
        for flav in ['u','ub','d','db','s','sb']:
            iflav+=1
            ipar=-1
            for par in ['N0','a0','b0','c0','d0','N1','a1','b1','c1','d1']:
                ipar+=1
                if '%s %s 1'%(flav,par) in conf['params']['sivers']:
                    conf['sivers'].shape1[iflav][ipar] = conf['params']['sivers']['%s %s 1'%(flav,par)]['value']
                if '%s %s 2'%(flav,par) in conf['params']['sivers']:
                    conf['sivers'].shape2[iflav][ipar] = conf['params']['sivers']['%s %s 2'%(flav,par)]['value']

        conf['sivers'].setup()

    def set_boermulders_params(self):
        self.set_constraits('boermulders')

        conf['boermulders']._widths1_uv  = conf['params']['boermulders']['widths1_uv']['value']
        conf['boermulders']._widths1_dv  = conf['params']['boermulders']['widths1_dv']['value']
        conf['boermulders']._widths1_sea = conf['params']['boermulders']['widths1_sea']['value']

        conf['boermulders']._widths2_uv  = conf['params']['boermulders']['widths2_uv']['value']
        conf['boermulders']._widths2_dv  = conf['params']['boermulders']['widths2_dv']['value']
        conf['boermulders']._widths2_sea = conf['params']['boermulders']['widths2_sea']['value']

        iflav=0
        for flav in ['u','ub','d','db','s','sb']:
            iflav+=1
            ipar=-1
            for par in ['N0','a0','b0','c0','d0','N1','a1','b1','c1','d1']:
                ipar+=1
                if '%s %s 1'%(flav,par) in conf['params']['boermulders']:
                    conf['boermulders'].shape1[iflav][ipar] = conf['params']['boermulders']['%s %s 1'%(flav,par)]['value']
                if '%s %s 2'%(flav,par) in conf['params']['boermulders']:
                    conf['boermulders'].shape2[iflav][ipar] = conf['params']['boermulders']['%s %s 2'%(flav,par)]['value']

        conf['boermulders'].setup()

    def set_ffpi_params(self):
        self.set_constraits('ffpi')
        conf['ffpi']._widths1_fav  = conf['params']['ffpi']['widths1_fav']['value']
        conf['ffpi']._widths1_ufav = conf['params']['ffpi']['widths1_ufav']['value']
        conf['ffpi']._widths2_fav  = conf['params']['ffpi']['widths2_fav']['value']
        conf['ffpi']._widths2_ufav = conf['params']['ffpi']['widths2_ufav']['value']
        conf['ffpi'].setup()

    def set_ffk_params(self):
        self.set_constraits('ffk')
        conf['ffk']._widths1_fav   = conf['params']['ffk']['widths1_fav']['value']
        conf['ffk']._widths1_ufav  = conf['params']['ffk']['widths1_ufav']['value']
        conf['ffk']._widths2_fav   = conf['params']['ffk']['widths2_fav']['value']
        conf['ffk']._widths2_ufav  = conf['params']['ffk']['widths2_ufav']['value']
        conf['ffk'].setup()

    def set_collinspi_params(self):
        self.set_constraits('collinspi')
        conf['collinspi']._widths1_fav  = conf['params']['collinspi']['widths1_fav']['value']
        conf['collinspi']._widths1_ufav = conf['params']['collinspi']['widths1_ufav']['value']
        conf['collinspi']._widths2_fav  = conf['params']['collinspi']['widths2_fav']['value']
        conf['collinspi']._widths2_ufav = conf['params']['collinspi']['widths2_ufav']['value']

        iflav=0
        for flav in ['u','ub','d','db','s','sb']:
            iflav+=1
            ipar=-1
            for par in ['N0','a0','b0','c0','d0','N1','a1','b1','c1','d1']:
                ipar+=1
                if '%s %s 1'%(flav,par) in conf['params']['collinspi']:
                    conf['collinspi'].shape1[iflav][ipar] = conf['params']['collinspi']['%s %s 1'%(flav,par)]['value']
                if '%s %s 2'%(flav,par) in conf['params']['collinspi']:
                    conf['collinspi'].shape2[iflav][ipar] = conf['params']['collinspi']['%s %s 2'%(flav,par)]['value']
        conf['collinspi'].setup()

    def set_collinsk_params(self):
        self.set_constraits('collinsk')
        conf['collinsk']._widths1_fav   = conf['params']['collinsk']['widths1_fav']['value']
        conf['collinsk']._widths1_ufav  = conf['params']['collinsk']['widths1_ufav']['value']
        conf['collinsk']._widths2_fav   = conf['params']['collinsk']['widths2_fav']['value']
        conf['collinsk']._widths2_ufav  = conf['params']['collinsk']['widths2_ufav']['value']
        iflav=0
        for flav in ['u','ub','d','db','s','sb']:
            iflav+=1
            ipar=-1
            for par in ['N0','a0','b0','c0','d0','N1','a1','b1','c1','d1']:
                ipar+=1
                if '%s %s 1'%(flav,par) in conf['params']['collinsk']:
                    conf['collinsk'].shape1[iflav][ipar] = conf['params']['collinsk']['%s %s 1'%(flav,par)]['value']
                if '%s %s 2'%(flav,par) in conf['params']['collinsk']:
                    conf['collinsk'].shape2[iflav][ipar] = conf['params']['collinsk']['%s %s 2'%(flav,par)]['value']
        conf['collinsk'].setup()

    def set_Htildepi_params(self):
            self.set_constraits('Htildepi')
            conf['Htildepi']._widths1_fav  = conf['params']['Htildepi']['widths1_fav']['value']
            conf['Htildepi']._widths1_ufav = conf['params']['Htildepi']['widths1_ufav']['value']
            conf['Htildepi']._widths2_fav  = conf['params']['Htildepi']['widths2_fav']['value']
            conf['Htildepi']._widths2_ufav = conf['params']['Htildepi']['widths2_ufav']['value']

            iflav=0
            for flav in ['u','ub','d','db','s','sb']:
                iflav+=1
                ipar=-1
                for par in ['N0','a0','b0','c0','d0','N1','a1','b1','c1','d1']:
                    ipar+=1
                    if '%s %s 1'%(flav,par) in conf['params']['Htildepi']:
                        conf['Htildepi'].shape1[iflav][ipar] = conf['params']['Htildepi']['%s %s 1'%(flav,par)]['value']
                    if '%s %s 2'%(flav,par) in conf['params']['Htildepi']:
                        conf['Htildepi'].shape2[iflav][ipar] = conf['params']['Htildepi']['%s %s 2'%(flav,par)]['value']
            conf['Htildepi'].setup()

    def set_Htildek_params(self):
            self.set_constraits('Htildek')
            conf['Htildek']._widths1_fav   = conf['params']['Htildek']['widths1_fav']['value']
            conf['Htildek']._widths1_ufav  = conf['params']['Htildek']['widths1_ufav']['value']
            conf['Htildek']._widths2_fav   = conf['params']['Htildek']['widths2_fav']['value']
            conf['Htildek']._widths2_ufav  = conf['params']['Htildek']['widths2_ufav']['value']
            iflav=0
            for flav in ['u','ub','d','db','s','sb']:
                iflav+=1
                ipar=-1
                for par in ['N0','a0','b0','c0','d0','N1','a1','b1','c1','d1']:
                    ipar+=1
                    if '%s %s 1'%(flav,par) in conf['params']['Htildek']:
                        conf['Htildek'].shape1[iflav][ipar] = conf['params']['Htildek']['%s %s 1'%(flav,par)]['value']
                    if '%s %s 2'%(flav,par) in conf['params']['Htildek']:
                        conf['Htildek'].shape2[iflav][ipar] = conf['params']['Htildek']['%s %s 2'%(flav,par)]['value']
            conf['Htildek'].setup()

    #--from here stuff with DGLAP

    def set_params(self,dist,FLAV,PAR):

        #--setup the constraints
        for flav in FLAV:
            for par in PAR:
                if flav+' '+par not in conf['params'][dist]: continue
                if conf['params'][dist][flav+' '+par]['fixed']==True: continue
                if conf['params'][dist][flav+' '+par]['fixed']==False: continue
                reference_flav=conf['params'][dist][flav+' '+par]['fixed']
                conf['params'][dist][flav+' '+par]['value']=conf['params'][dist][reference_flav]['value']
  
        #--update values at the class
        for flav in FLAV:
            idx=0
            for par in PAR:
                if  flav+' '+par in conf['params'][dist]:
                    conf[dist].params[flav][idx]=conf['params'][dist][flav+' '+par]['value'] 
                else:
                    conf[dist].params[flav][idx]=0
                idx+=1
  
        conf[dist].setup()
  
        #--update values at conf
        for flav in FLAV:
            idx=0
            for par in PAR:
                if  flav+' '+par in conf['params'][dist]:
                    conf['params'][dist][flav+' '+par]['value']= conf[dist].params[flav][idx] 
                idx+=1

    def set_transversityp_params(self):
        self.set_constraits('transversity')

        conf['transversity+']._widths1_uv  = conf['params']['transversity+']['widths1_uv']['value']
        conf['transversity+']._widths1_dv  = conf['params']['transversity+']['widths1_dv']['value']
        conf['transversity+']._widths1_sea = conf['params']['transversity+']['widths1_sea']['value']

        conf['transversity+']._widths2_uv  = conf['params']['transversity+']['widths2_uv']['value']
        conf['transversity+']._widths2_dv  = conf['params']['transversity+']['widths2_dv']['value']
        conf['transversity+']._widths2_sea = conf['params']['transversity+']['widths2_sea']['value']

        FLAV=['g1','uv1','dv1','sea1','sea2','db1','ub1','s1','sb1']
        PAR=['N','a','b','c','d']
        self.set_params('transversity+',FLAV,PAR)

    def set_collinspip_params(self):
        self.set_constraits('collinspi+')
        conf['collinspi+']._widths1_fav  = conf['params']['collinspi+']['widths1_fav']['value']
        conf['collinspi+']._widths1_ufav = conf['params']['collinspi+']['widths1_ufav']['value']
        conf['collinspi+']._widths2_fav  = conf['params']['collinspi+']['widths2_fav']['value']
        conf['collinspi+']._widths2_ufav = conf['params']['collinspi+']['widths2_ufav']['value']
        FLAV=['g1','u1','d1','s1','c1','b1']
        FLAV.extend(['ub1','db1','sb1','cb1','bb1'])
        PAR=['N','a','b','c','d']
        self.set_params('collinspi+',FLAV,PAR)






