"""
Model exported as python.
Name : Importar con reproyeccion y recorte (Vectorial)
Group : Cargar y exportar datos
With QGIS : 31601
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterFeatureSource
from qgis.core import QgsProcessingParameterCrs
from qgis.core import QgsProcessingParameterFeatureSink
from qgis.core import QgsProcessingParameterBoolean
import processing


class ImportarConReproyeccionYRecorteVectorial(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFeatureSource('da', 'Layer', types=[QgsProcessing.TypeVectorAnyGeometry], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSource('Overlaylayer', 'Overlay layer', types=[QgsProcessing.TypeVectorAnyGeometry], defaultValue=None))
        self.addParameter(QgsProcessingParameterCrs('CRS', 'CRS', defaultValue='EPSG:4326'))
        self.addParameter(QgsProcessingParameterFeatureSink('Output', 'output', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
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

        # Reproject layer
        alg_params = {
            'INPUT': parameters['da'],
            'OPERATION': '',
            'TARGET_CRS': parameters['CRS'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ReprojectLayer'] = processing.run('native:reprojectlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Clip
        alg_params = {
            'INPUT': outputs['ReprojectLayer']['OUTPUT'],
            'OVERLAY': outputs['ReprojectOverlay']['OUTPUT'],
            'OUTPUT': parameters['Output']
        }
        outputs['Clip'] = processing.run('native:clip', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Output'] = outputs['Clip']['OUTPUT']
        return results

    def name(self):
        return 'Importar con reproyeccion y recorte (Vectorial)'

    def displayName(self):
        return 'Importar con reproyeccion y recorte (Vectorial)'

    def group(self):
        return 'Cargar y exportar datos'

    def groupId(self):
        return 'Cargar y exportar datos'

    def createInstance(self):
        return ImportarConReproyeccionYRecorteVectorial()
