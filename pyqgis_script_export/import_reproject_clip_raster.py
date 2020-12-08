"""
Model exported as python.
Name : Importar con reproyeccion y recorte (Raster)
Group : Cargar y exportar datos
With QGIS : 31601
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterFeatureSource
from qgis.core import QgsProcessingParameterCrs
from qgis.core import QgsProcessingParameterRasterLayer
from qgis.core import QgsProcessingParameterRasterDestination
from qgis.core import QgsProcessingParameterBoolean
import processing


class ImportarConReproyeccionYRecorteRaster(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFeatureSource('Overlaylayer', 'Overlay layer', types=[QgsProcessing.TypeVectorAnyGeometry], defaultValue=None))
        self.addParameter(QgsProcessingParameterCrs('CRS', 'Output CRS', defaultValue='EPSG:4326'))
        self.addParameter(QgsProcessingParameterRasterLayer('Layer', 'Layer', defaultValue=None))
        self.addParameter(QgsProcessingParameterCrs('RasterinputCRS', 'Raster input CRS', defaultValue='EPSG:4326'))
        self.addParameter(QgsProcessingParameterRasterDestination('Output', 'output', createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterBoolean('VERBOSE_LOG', 'Verbose logging', optional=True, defaultValue=False))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(3, model_feedback)
        results = {}
        outputs = {}

        # Reproject overlay
        alg_params = {
            'INPUT': parameters['Overlaylayer'],
            'OPERATION': '',
            'TARGET_CRS': parameters['CRS'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ReprojectOverlay'] = processing.run('native:reprojectlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Warp (reproject)
        alg_params = {
            'DATA_TYPE': 0,
            'EXTRA': '',
            'INPUT': parameters['Layer'],
            'MULTITHREADING': False,
            'NODATA': -9999,
            'OPTIONS': '',
            'RESAMPLING': 0,
            'SOURCE_CRS': parameters['RasterinputCRS'],
            'TARGET_CRS': parameters['CRS'],
            'TARGET_EXTENT': None,
            'TARGET_EXTENT_CRS': None,
            'TARGET_RESOLUTION': None,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['WarpReproject'] = processing.run('gdal:warpreproject', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Clip raster by mask layer
        alg_params = {
            'ALPHA_BAND': False,
            'CROP_TO_CUTLINE': True,
            'DATA_TYPE': 0,
            'EXTRA': '',
            'INPUT': outputs['WarpReproject']['OUTPUT'],
            'KEEP_RESOLUTION': True,
            'MASK': outputs['ReprojectOverlay']['OUTPUT'],
            'MULTITHREADING': False,
            'NODATA': -9999,
            'OPTIONS': '',
            'SET_RESOLUTION': False,
            'SOURCE_CRS': parameters['CRS'],
            'TARGET_CRS': parameters['CRS'],
            'X_RESOLUTION': None,
            'Y_RESOLUTION': None,
            'OUTPUT': parameters['Output']
        }
        outputs['ClipRasterByMaskLayer'] = processing.run('gdal:cliprasterbymasklayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Output'] = outputs['ClipRasterByMaskLayer']['OUTPUT']
        return results

    def name(self):
        return 'Importar con reproyeccion y recorte (Raster)'

    def displayName(self):
        return 'Importar con reproyeccion y recorte (Raster)'

    def group(self):
        return 'Cargar y exportar datos'

    def groupId(self):
        return 'Cargar y exportar datos'

    def createInstance(self):
        return ImportarConReproyeccionYRecorteRaster()
