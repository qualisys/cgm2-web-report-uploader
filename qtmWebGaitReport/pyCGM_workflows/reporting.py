from pyCGM2.Report import normativeDatasets
from pyCGM2.Lib import analysis, plot
from pyCGM2.qtm import qtmTools
from pyCGM2 import enums
from pyCGM2 import log
from qtmWebGaitReport.convert_report_json_to_regression_test_xml import save_session_data_xml_from
from qtmWebGaitReport import qtmFilters
from qtmWebGaitReport import utils
import matplotlib.pyplot as plt
import logging
import warnings
import os

log.setLoggingLevel(logging.INFO)

warnings.simplefilter(action='ignore', category=FutureWarning)


def get_modelled_trials(session_xml, measurement_type):
    modelled_trials = []
    dynamicMeasurements = qtmTools.findDynamic(session_xml)
    for dynamicMeasurement in dynamicMeasurements:
        if qtmTools.isType(dynamicMeasurement, measurement_type):
            filename = qtmTools.getFilename(dynamicMeasurement)
            modelled_trials.append(filename)
    return modelled_trials


def create_subject_metadata(session_xml, measurement_type):
    return {
        "patientName": session_xml.find("Last_name").text + " " + session_xml.find("First_name").text,
        "patientID": session_xml.find("Patient_ID").text,
        "bodyHeight": session_xml.find("Height").text,
        "bodyWeight": session_xml.find("Weight").text,
        "diagnosis": session_xml.find("Diagnosis").text,
        "dob": session_xml.find("Date_of_birth").text,
        "sex": session_xml.find("Sex").text,
        "test condition": measurement_type,
        "gmfcs": session_xml.find("Gross_Motor_Function_Classification").text,
        "fms": session_xml.find("Functional_Mobility_Scale").text}


def create_web_report(session_xml, data_path):

    measurement_types = qtmTools.detectMeasurementType(session_xml)
    for measurement_type in measurement_types:

        modelledTrials = get_modelled_trials(session_xml, measurement_type)

        subjectMd = create_subject_metadata(session_xml, measurement_type)

        sessionDate = utils.get_creation_date(session_xml)

        report = qtmFilters.WebReportFilter(
            data_path, modelledTrials, subjectMd, sessionDate)
        # report.exportJson()
        save_session_data_xml_from(report.getReportData())
        report.upload()
        logging.info("qualisys Web Report exported")


def process_pdf_report(data_path, modelled_trials, title, model,  normative_dataset, point_suffix=None):
    analysisInstance = analysis.makeAnalysis(
        data_path + "\\", modelled_trials,
        subjectInfo=None,
        experimentalInfo=None,
        modelInfo=None,
        pointLabelSuffix=None)

    # spatiotemporal
    plot.plot_spatioTemporal(data_path, analysisInstance,
                             exportPdf=True,
                             outputName=title,
                             show=None,
                             title=title)

    # Kinematics
    if model.m_bodypart in [enums.BodyPart.LowerLimb, enums.BodyPart.LowerLimbTrunk, enums.BodyPart.FullBody]:
        plot.plot_DescriptiveKinematic(data_path, analysisInstance, "LowerLimb",
                                       normative_dataset,
                                       exportPdf=True,
                                       outputName=title,
                                       pointLabelSuffix=point_suffix,
                                       show=False,
                                       title=title)

        plot.plot_ConsistencyKinematic(data_path, analysisInstance, "LowerLimb",
                                       normative_dataset,
                                       exportPdf=True,
                                       outputName=title,
                                       pointLabelSuffix=point_suffix,
                                       show=False,
                                       title=title)
    if model.m_bodypart in [enums.BodyPart.LowerLimbTrunk, enums.BodyPart.FullBody]:
        plot.plot_DescriptiveKinematic(data_path, analysisInstance, "Trunk",
                                       normative_dataset,
                                       exportPdf=True,
                                       outputName=title,
                                       pointLabelSuffix=point_suffix,
                                       show=False,
                                       title=title)

        plot.plot_ConsistencyKinematic(data_path, analysisInstance, "Trunk",
                                       normative_dataset,
                                       exportPdf=True,
                                       outputName=title,
                                       pointLabelSuffix=point_suffix,
                                       show=False,
                                       title=title)

    if model.m_bodypart in [enums.BodyPart.UpperLimb, enums.BodyPart.FullBody]:
        pass  # TODO plot upperlimb panel

    # Kinetics
    if model.m_bodypart in [enums.BodyPart.LowerLimb, enums.BodyPart.LowerLimbTrunk, enums.BodyPart.FullBody]:
        plot.plot_DescriptiveKinetic(data_path, analysisInstance, "LowerLimb",
                                     normative_dataset,
                                     exportPdf=True,
                                     outputName=title,
                                     pointLabelSuffix=point_suffix,
                                     show=False,
                                     title=title)

        plot.plot_ConsistencyKinetic(data_path, analysisInstance, "LowerLimb",
                                     normative_dataset,
                                     exportPdf=True,
                                     outputName=title,
                                     pointLabelSuffix=point_suffix,
                                     show=False,
                                     title=title)

    # MAP
    plot.plot_MAP(data_path, analysisInstance,
                  normative_dataset,
                  exportPdf=True,
                  outputName=title, pointLabelSuffix=point_suffix,
                  show=False,
                  title=title)

    plt.show(False)


def create_pdf_report(session_xml, data_path, model):
    normative_dataset = normativeDatasets.Schwartz2008("Free")
    measurement_types = qtmTools.detectMeasurementType(session_xml)
    for measurement_type in measurement_types:

        modelledTrials = get_modelled_trials(session_xml, measurement_type)
        process_pdf_report(
            data_path, modelledTrials, measurement_type, model, normative_dataset)
