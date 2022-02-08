try:
    # use standard Python importlib if available (>Python3.7)
    import importlib.resources as importlib_resources
except ImportError:
    import importlib_resources

import sys
from pathlib import Path
from os import walk, mkdir

from xacro import process_file, open_output
from xacro.color import error
from xacro.xmlutils import xml

unicode = str
encoding = {}


def find_paths(robot_name, robot_family="bolt"):
    with importlib_resources.path(__package__, "utils.py") as p:
        package_dir = p.parent.absolute()

    resources_dir = package_dir / ("robot_properties_" + robot_family)
    dgm_yaml_path = (
        resources_dir
        / "dynamic_graph_manager"
        / ("dgm_parameters_" + robot_name + ".yaml")
    )
    urdf_path = resources_dir / (robot_name + ".urdf")
    simu_urdf_path = resources_dir / "bolt_passive_ankle.urdf"
    srdf_path = resources_dir / "srdf" / (robot_family + ".srdf")
    ctrl_path = resources_dir / "impedance_ctrl.yaml"

    if not urdf_path.exists():
        build_xacro_files(resources_dir)

    paths = {
        "package": str(package_dir),
        "resources": str(resources_dir),
        "dgm_yaml": str(dgm_yaml_path),
        "srdf": str(srdf_path),
        "urdf": str(urdf_path),
        "simu_urdf": str(simu_urdf_path),
        "imp_ctrl_yaml": str(ctrl_path),
    }

    return paths


def build_xacro_files(resources_dir):
    """ Look for the xacro files and build them in the build folder. """
    import pathlib
    print("Searching XACRO files in: %s" % resources_dir)
    build_folder = resources_dir
    xacro_files = []
    print("XACRO FILES:")
    for (root, _, files) in walk(str(Path(resources_dir) / "xacro")):
        for afile in files:
            print("- %s" % afile)
            if afile.endswith(".urdf.xacro"):
                xacro_files.append(str(Path(root) / afile))
                print("- %s" % afile)

    if not Path(build_folder).exists():
        mkdir(build_folder)
        print("Build folder [%s]" % build_folder)

    for xacro_file in xacro_files:
        for xacro_file in xacro_files:
            # Generated file name
            generated_urdf_path = str(
                Path(build_folder) / Path(xacro_file).stem
            )
            build_single_xacro_file(xacro_file, generated_urdf_path)
            print("Build: %s" % generated_urdf_path)


def build_single_xacro_file(input_path, output_path):
    print("building xacro file (", input_path, ") into (", output_path, ")")
    try:
        # open and process file
        doc = process_file(input_path)
        # open the output file
        out = open_output(output_path)

    except xml.parsers.expat.ExpatError as e:
        error("XML parsing error: %s" % unicode(e), alt_text=None)
        sys.exit(2)

    except Exception as e:
        msg = unicode(e)
        if not msg:
            msg = repr(e)
        error(msg)
        sys.exit(2)  # gracefully exit with error condition

    # Hi i was not here before :)
    # write output
    out.write(doc.toprettyxml(indent="  ", **encoding))
    # only close output file, but not stdout
    out.close()
