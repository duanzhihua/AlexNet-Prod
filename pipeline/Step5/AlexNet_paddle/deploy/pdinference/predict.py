import os
import paddle
from paddle import inference
import numpy as np
from PIL import Image

from reprod_log import ReprodLogger

from preprocess import ResizeImage, CenterCropImage, NormalizeImage, ToCHW, Compose


def load_predictor(model_file_path, params_file_path, args):
    config = inference.Config(model_file_path, params_file_path)
    if args.use_gpu:
        config.enable_use_gpu(1000, 0)
        if args.use_tensorrt:
            if hasattr(args, 'precision'):
                if args.precision == "fp16" and args.use_tensorrt:
                    precision = inference.PrecisionType.Half
                elif args.precision == "int8":
                    precision = inference.PrecisionType.Int8
                else:
                    precision = inference.PrecisionType.Float32
            else:
                precision = inference.PrecisionType.Float32

            config.enable_tensorrt_engine(
                workspace_size=1 << 30,
                precision_mode=precision,
                max_batch_size=args.max_batch_size,
                min_subgraph_size=args.min_subgraph_size)
    else:
        config.disable_gpu()
        if args.use_mkldnn:
            config.enable_mkldnn()
            config.set_cpu_math_library_num_threads(args.cpu_threads)

    # enable memory optim
    config.enable_memory_optim()
    config.disable_glog_info()

    config.switch_use_feed_fetch_ops(False)
    config.switch_ir_optim(True)

    # create predictor
    predictor = inference.create_predictor(config)
    return predictor


def get_args(add_help=True):
    import argparse

    def str2bool(v):
        return v.lower() in ("true", "t", "1")

    parser = argparse.ArgumentParser(
        description='PaddlePaddle Classification Training', add_help=add_help)

    parser.add_argument(
        '--model-dir', default=None, help='inference model dir')
    parser.add_argument(
        '--use-gpu', default=False, type=str2bool, help='use_gpu')
    parser.add_argument(
        '--use-tensorrt', default=False, type=str2bool, help='use_trt')
    parser.add_argument(
        '--use-mkldnn', default=False, type=str2bool, help='use_mkldnn')
    parser.add_argument('--precision', default='fp32', help='precision')
    parser.add_argument(
        '--min-subgraph-size', default=15, type=int, help='min_subgraph_size')
    parser.add_argument(
        '--max-batch-size', default=16, type=int, help='max_batch_size')
    parser.add_argument(
        '--cpu-threads', default=10, type=int, help='cpu-threads')

    parser.add_argument(
        '--resize-size', default=256, type=int, help='resize_size')
    parser.add_argument('--crop-size', default=224, type=int, help='crop_szie')
    parser.add_argument('--img-path', default='./images/demo.jpg')

    parser.add_argument(
        '--benchmark', default=True, type=str2bool, help='benchmark')
    args = parser.parse_args()
    return args


def predict(args):
    predictor = load_predictor(
        os.path.join(args.model_dir, "inference.pdmodel"),
        os.path.join(args.model_dir, "inference.pdiparams"), args)

    input_names = predictor.get_input_names()
    input_tensor = predictor.get_input_handle(input_names[0])

    output_names = predictor.get_output_names()
    output_tensor = predictor.get_output_handle(output_names[0])

    eval_transforms = Compose([
        ResizeImage(args.resize_size), CenterCropImage(args.crop_size),
        NormalizeImage(), ToCHW()
    ])

    with open(args.img_path, 'rb') as f:
        img = Image.open(f)
        img = img.convert('RGB')

    img = eval_transforms(img)
    img = np.expand_dims(img, axis=0)

    input_tensor.copy_from_cpu(img)
    predictor.run()
    output = output_tensor.copy_to_cpu()
    output = output.flatten()

    class_id = output.argmax()
    prob = output[class_id]
    print(f"class_id: {class_id}, prob: {prob}")
    return output


if __name__ == "__main__":
    args = get_args()
    output = predict(args)

    reprod_logger = ReprodLogger()
    reprod_logger.add("output", output)
    reprod_logger.save("output_inference_engine.npy")
