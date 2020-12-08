"""
Model exported as python.
Name : Area por categoria en buffer (poligono)
Group : Transformaciones vectoriales basicas
With QGIS : 31601
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterBoolean
from qgis.core import QgsProcessingParameterFeatureSink
from qgis.core import QgsProperty
import processing


class AreaPorCategoriaEnBufferPoligono(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('Area', 'Capa vectorial', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('Categorias', 'Categorias', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterBoolean('VERBOSE_LOG', 'Verbose logging', optional=True, defaultValue=False))
        self.addParameter(QgsProcessingParameterFeatureSink('Area_by_category', 'area_by_category', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(5, model_feedback)
        results = {}
        outputs = {}

        # Buffer
        alg_params = {
            'DISSOLVE': False,
            'DISTANCE': QgsProperty.fromExpression('"buff_dist"'),
            'END_CAP_STYLE': 0,
            'INPUT': parameters['Area'],
            'JOIN_STYLE': 0,
            'MITER_LIMIT': 2,
            'SEGMENTS': 5,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Buffer'] = processing.run('native:buffer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Symmetrical difference
        alg_params = {
            'INPUT': outputs['Buffer']['OUTPUT'],
            'OVERLAY': parameters['Area'],
            'OVERLAY_FIELDS_PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['SymmetricalDifference'] = processing.run('native:symmetricaldifference', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Join attributes by location
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'INPUT': outputs['SymmetricalDifference']['OUTPUT'],
            'JOIN': parameters['Area'],
            'JOIN_FIELDS': [''],
            'METHOD': 0,
            'PREDICATE': [3],
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByLocation'] = processing.run('native:joinattributesbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Clip
        alg_params = {
            'INPUT': parameters['Categorias'],
            'OVERLAY': outputs['JoinAttributesByLocation']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Clip'] = processing.run('native:clip', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Field calculator
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'area_m',
            'FIELD_PRECISION': 1,
            'FIELD_TYPE': 0,
            'FORMULA': '$area',
            'INPUT': outputs['Clip']['OUTPUT'],
            'OUTPUT': parameters['Area_by_category']
        }
        outputs['FieldCalculator'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Area_by_category'] = outputs['FieldCalculator']['OUTPUT']
        return results

    def name(self):
        return 'Area por categoria en buffer (poligono)'

    def displayName(self):
        return 'Area por categoria en buffer (poligono)'

    def group(self):
        return 'Transformaciones vectoriales basicas'

    def groupId(self):
        return 'Transformaciones vectoriales basicas'

    def shortHelpString(self):
        return """<html><body><h2>Algorithm description</h2>
<p>Para una serie de polígonos dados el algorítmo devuelve el área (dividida por categorías) que se encuentra dentro de una distancia concreta al perímetro de los polígonos de interés.

La distancia del polígono queda definida en base a un campo de la tabla de atributos de la capa de entrada llamado "buff_dist"</p>
<h2>Input parameters</h2>
<h3>Capa vectorial</h3>
<p></p>
<h3>Categorias</h3>
<p></p>
<h3>Verbose logging</h3>
<p></p>
<h3>area_by_category</h3>
<p></p>
<h2>Outputs</h2>
<h3>area_by_category</h3>
<p></p>
<br></body></html>"""

    def createInstance(self):
        return AreaPorCategoriaEnBufferPoligono()
