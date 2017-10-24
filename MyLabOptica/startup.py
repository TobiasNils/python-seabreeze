# -*- coding: utf-8 -*-
"""
My custom startup file

Created on Tue Dec 13 15:06:42 2016

@author: nils
"""
import numpy as np
class MyFuncs():
        
    def Loss(i, i0):
        try:
            assert(type(i0)==np.float64 or type(i0)==np.ndarray or type(i0)==float)
            assert(type(i)==np.float64 or type(i)==np.ndarray  or type(i)==float)   
            L = -10*np.log10(i/i0)
            try:
                len(L)
                return np.array(L)
            except TypeError:    
                return float(L)
        except AssertionError:
            try:
                i, i0 = np.array(i), np.array(i0)
                L = -10*np.log10(np.divide(i/i0))
                try:
                    len(L)
                    return np.array(L)
                except TypeError:    
                    return float(L)
            except:
                print('invalid input: float or array input with equal length expected')
            
    def Absorbance(i, i0):
        try:
            assert(type(i0)==np.float64 or type(i0)==np.ndarray or type(i0)==float)
            assert(type(i)==np.float64 or type(i)==np.ndarray  or type(i)==float)   
            
            with np.errstate(divide='ignore', invalid='ignore'):
                in_out = np.array(np.true_divide(i,i0))
            L = -np.log10(in_out)
            
            try:
                
                len(L)
                return np.array(L)

                undefined = list(np.where(L == np.inf)[0])                    
                undefined.append(list(np.where(L== -np.inf)[0]))                   
                undefined.append(list(np.where(L== np.nan)[0]))
                
                for i in undefined:
                    L[i]=0
                            
            except TypeError:    
                L = float(L)
                if L==np.inf or L==-np.inf:
                    return np.nan
                else:
                    return L
        except AssertionError:
            try:
                i, i0 = np.array(i), np.array(i0)                
                
                with np.errstate(divide='ignore', invalid='ignore'):
                    in_out = np.array(np.true_divide(i,i0))
                L = -np.log10(in_out)
                
                try:
                    len(L)
                    return np.array(L)
                    undefined = list(np.where(L == np.inf)[0])                    
                    undefined.append(list(np.where(L== -np.inf)[0]))                   
                    undefined.append(list(np.where(L== np.nan)[0]))
                    
                    for i in undefined:
                        L[i]=0
                                
                except TypeError:    
                    L = float(L)
                    if L==np.inf or L==-np.inf:
                        return np.nan
                    else:
                        return L


            except:
                print('invalid input: float input expected')
                
    def load_dict(filename):
        # load dictionary in 'filename.npy' saved with np.save
        dictionary = np.load(str(filename)+'.npy').item()
        print('loaded dictionary with', dictionary.keys())
        return dictionary
    
    def dataset_mean(dataset):
        data = []
        for key in dataset.keys():
            data.append(dataset[key]['i']['mean spec']-dataset[key]['i_dark']['mean spec'])
        yerr = np.nanstd(data, axis=0)
        mean = np.nanmean(data, axis=0)
        
        return {'mean spec':mean, 'std dev':yerr}
    
    def linear_fit( x, y, points, fig = None):
                
        from scipy.stats import linregress
        points=points
        r_squared = 0.
        best = {}
        best['r_squared'] = r_squared
        
        for i in range(len(x)-points+1):
            
            j = points+i               
            fit=linregress(x[i:j], y[i:j])
            r_squared = fit[2]**2
                        
            if r_squared > best['r_squared']:
                best['i'] = i
                best['fit'] = fit
                best['r_squared'] = r_squared
            else:
                pass

        x_range, y_range = x[best['i']:best['i']+points],y[best['i']:best['i']+points]
        
        SSx = sum([(xi-np.mean(x_range))**2 for xi in x_range])
        SSE = sum(
                [(yi-
                (best['fit'][1]+best['fit'][0]*x_range[y_range.index(yi)]))**2 for yi in y_range]
                 )
        s_yx = np.sqrt(SSE/(points-2))
        sigma_intercept = s_yx*np.sqrt(1/points + np.mean(x_range)**2/SSx)
        print(SSx,SSE,s_yx,sigma_intercept)
        LOD = 10*sigma_intercept/ best['fit'][0]  
        
        print('slope', best['fit'][0], '+/-', best['fit'][4], '\nLOD = ', LOD)
        if fig==None:
            pass
        else:
            name = 'best linear fit using ' +str(points)+' points:\nslope'+ str(best['fit'][0]) + '+/-' + str(best['fit'][4])
            fig.line(name, x[best['i']:best['i']+points],[best['fit'][0]*value+best['fit'][1] for value in x[best['i']:best['i']+points]], pen='r')
        
        return {'slope':best['fit'][0],
                'intersect':best['fit'][1],
                'err':best['fit'][-1],
                'LOD':LOD}
    
    def val_at_wl(spec, wl, wl_key):
         
        ii = np.where(np.int_(wl_binning[wl_key]) == wl)
        print(ii)
        val = np.nanmean([spec[i] for i in ii])
        val_dev = np.nanstd([spec[i] for i in ii])
        print(val, ' +/- ', val_dev)
        return val
    
    def wl_index(wl_key, wl_array):
        
        ii = np.where(np.int_(wl_array) == wl_key)
        return ii[0][0]
    
    def save_wl(db):
        np.save('MyLabOptica/database_wl_binning', db)
         

#==============================================================================
# Import data from text-files
#==============================================================================
class ImportTXT():
    """
    Utensiles for importing data from *.txt files save in the format used by 
    SpectraSuite, former Ocean Optics data acquisition Software, to python
    dictionaries
    """
    def __init__(self,skip_lines_start = 17, skip_lines_end=1,separator = ",",
                 delimiter ='\t'):
        
        # init variables 
       
        self.skip_lines_start = skip_lines_start 
        self.skip_lines_end = skip_lines_end
        self.separator = separator
        self.delimiter = delimiter
        self.imported_data = {}    
        
    def do_import(self, files, encoding = 'utf-8'):
        # uses the parameteres and directories provided using the ImportTool 
        # widget and loads the data into the spyder/python3 workspace
        
        print('importing from ...', files)
        self.imported_data = {} 
        for file in files:
            
            unconverted_lines = open(file, encoding = encoding).read().splitlines()
            header = unconverted_lines[0:self.skip_lines_start]
            lines = []
            
            if self.separator==',':
                for line in unconverted_lines:
                    lines.append(line.replace(",", "."))
            else:
                lines = unconverted_lines
                        
            if self.skip_lines_end == 0:         
                data = lines[self.skip_lines_start:]
                
            else:
                data = lines[self.skip_lines_start:-self.skip_lines_end]
            
            self.imported_data[file] = {}
            self.imported_data[file]['details']=header[:-1]
            if encoding=='latin-1':
                IT = float(header[8].split('Tiempo de integración (usec): ')[1].split(
                    ' (QEPB0195)')[0])
            else:
                IT = float(header[8].split('Integration Time (usec): ')[1].split(
                    ' (QEPB0152)')[0])
            self.imported_data[file]['IT/ms']= IT/1000
            col1 = [float(line.split(self.delimiter)[0]) for line in data]
            col2 = [float(line.split(self.delimiter)[1]) for line in data]
            self.imported_data[file]['data']= [np.array(col1), np.array(col2)]
        
        return self.imported_data