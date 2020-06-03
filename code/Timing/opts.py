import argparse

def parse_opt():
    parser = argparse.ArgumentParser()
    # Overall settings
    parser.add_argument(
        '--mode',
        type=str,
        default='train')
    parser.add_argument(
        '--checkpoint_path',
        type=str,
        default='./checkpoint')
    parser.add_argument(
        '--model',
        type=str,
        default='lstm')
    parser.add_argument(
        '--training_lr',
        type=float,
        default=0.001)
    parser.add_argument(
        '--weight_decay',
        type=float,
        default=1e-4)

    parser.add_argument(
        '--train_epochs',
        type=int,
        default=9)
    parser.add_argument(
        '--batch_size',
        type=int,
        default=8)
    parser.add_argument(
        '--step_size',
        type=int,
        default=7)
    parser.add_argument(
        '--step_gamma',
        type=float,
        default=0.1)
    
    # Overall Dataset settings
    parser.add_argument(
        '--train_feature',
        type=str,
        default="./data/city_feature_timing_train.csv")
    parser.add_argument(
        '--test_feature',
        type=str,
        default="./data/city_feature_timing_test.csv")
    parser.add_argument(
        '--train_date',
        type=str,
        default="./data/train_date.csv")
    parser.add_argument(
        '--test_date',
        type=str,
        default="./data/test_date.csv")
    parser.add_argument(
        '--adj_path',
        type=str,
        default="./data/covid/")
    parser.add_argument(
        '--city_id',
        type=str,
        default="D:\COVID-19\data\china_location_id_2015.csv")
    parser.add_argument(
        '--T',
        type=int,
        default=7
    parser.add_argument(
        '--fealen',
        type=int,
        default=7
    parser.add_argument(
        '--nodes',
        type=int,
        default=361)
    parser.add_argument(
        '--gcn_hidden_dim',
        type=int,
        default=16)
    parser.add_argument(
        '--hidden_dim',
        type=int,
        default=16)
    parser.add_argument(
        '--kernel_dim',
        type=int,
        default=10)

    # output result
    parser.add_argument(
        '--result_file',
        type=str,
        default="./output/result.csv")

    args = parser.parse_args()

    return args