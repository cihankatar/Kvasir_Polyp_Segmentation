import torch
import torch.nn as nn
import time

class conv_block(nn.Module):
    def __init__(self, in_c, out_c):
        super().__init__()
        
        self.conv_block=nn.Sequential(nn.Conv2d(in_c, out_c, kernel_size=3, padding=1),
                                     nn.BatchNorm2d(out_c),
                                     nn.Conv2d(out_c, out_c, kernel_size=3, padding=1),
                                     nn.BatchNorm2d(out_c),
                                     nn.ReLU())
        
        self.pool = nn.MaxPool2d((2, 2))
       
    def forward(self, inputs):
        conv_block_out=self.conv_block(inputs)

        return conv_block_out

class down(nn.Module):
    def __init__(self, in_c, out_c):
        super().__init__()

        self.conv = conv_block(in_c, out_c)
        self.pool = nn.MaxPool2d((2, 2))

    def forward(self, inputs):
        conv_block_out=self.conv(inputs)
        encoder_output = self.pool(conv_block_out)

        return conv_block_out, encoder_output


class up(nn.Module):
    def __init__(self, in_c, out_c):
        super().__init__()

        self.up   = nn.ConvTranspose2d(in_c, out_c, kernel_size=2, stride=2, padding=0)
        self.conv = conv_block(out_c+out_c, out_c)

    def forward(self, inputs, skip):
        conv_t_out = self.up(inputs)
        concat = torch.concat((conv_t_out,skip),dim=1)
        decoder_output = self.conv(concat)
        return decoder_output
    

class UNET(nn.Module):
    def __init__(self,n_classes):
        super().__init__()
        
        self.n_classes = n_classes
        #sigmoid_f      = nn.Sigmoid()
        #softmax_f      = nn.Softmax()

        size_en=[3,64,128,256,512]
        self.encoder_blocks = nn.ModuleList([down(in_f, out_f) for in_f, out_f in zip(size_en,size_en[1:])])

        self.b = conv_block(512, 1024)

        size_dec=[1024,512,256,128,64]
        self.decoder_blocks = nn.ModuleList([up(in_f, out_f) for in_f, out_f in zip(size_dec,size_dec[1:])])

        
        if self.n_classes > 1:

            self.outputs  = nn.Conv2d(64, 2, kernel_size=1, padding=0)
            #self.outputs = softmax_f(self.outputs)
        else:
            self.outputs  = nn.Conv2d(64, 1, kernel_size=1, padding=0)
            #self.outputs  = sigmoid_f(self.outputs)

    def forward(self, inputs):                      # 1x  3 x 128 x 128
        
        s1, p1 = self.encoder_blocks[0](inputs)     # 1x  64 x 128x128 ,  64  x 64x64
        s2, p2 = self.encoder_blocks[1](p1)         # 1x 128 x 64x64   ,  128 x 32x32
        s3, p3 = self.encoder_blocks[2](p2)         # 1x 256 x 32x32   ,  256 x 16x16
        s4, p4 = self.encoder_blocks[3](p3)         # 1x 512 x 16x16   ,  512 x 8x8

        b = self.b(p4)                              # 1x 1024 x 8x8

        d1 = self.decoder_blocks[0](b, s4)          # 1x 512 x  16x16
        d2 = self.decoder_blocks[1](d1, s3)         # 1x 256 x  32x32
        d3 = self.decoder_blocks[2](d2, s2)         # 1x 128 x  64x64
        d4 = self.decoder_blocks[3](d3, s1)         # 1x  64 x 128x128

        outputs = self.outputs(d4)                  # 1   64 x 128x128


        # import matplotlib.pyplot as plt 
        # import numpy as np
        
        # image =inputs[1,1]
        
        # enc1  = s1[1,1]
        # enc2  = s2[1,1]
        # enc3  = s3[1,1]
        # enc4  = s4[1,1]

        # bottle  = b[1,1]

        # dec1  = d1[1,1]
        # dec2  = d2[1,1]
        # dec3  = d3[1,1]
        # dec4  = d4[1,1]

        # output  = outputs[1,0]
        # output    = output > 0.5
        # output    = np.array(output, dtype=np.uint8)

        # plt.figure()
        # plt.subplot(3, 5, 1)
        # plt.imshow(image.detach().numpy(),cmap='gray')
        # plt.subplot(3, 5, 2)
        # plt.imshow(enc1.detach().numpy(),cmap='gray')
        # plt.subplot(3, 5, 3)
        # plt.imshow(enc2.detach().numpy(),cmap='gray')
        # plt.subplot(3, 5, 4)
        # plt.imshow(enc3.detach().numpy(),cmap='gray')
        # plt.subplot(3, 5, 5)
        # plt.imshow(enc4.detach().numpy(),cmap='gray')

        # plt.subplot(3, 5, 7)
        # plt.imshow(bottle.detach().numpy(),cmap='gray')

        # plt.subplot(3, 5, 11)
        # plt.imshow(dec1.detach().numpy(),cmap='gray')
        # plt.subplot(3, 5, 12)
        # plt.imshow(dec2.detach().numpy(),cmap='gray')
        # plt.subplot(3, 5, 13)
        # plt.imshow(dec3.detach().numpy(),cmap='gray')
        # plt.subplot(3, 5, 14)
        # plt.imshow(dec4.detach().numpy(),cmap='gray')
        # plt.subplot(3, 5, 15)
        # plt.imshow(output,cmap='gray')

        return outputs

if __name__ == "__main__":

    start=time.time()

    x = torch.randn((2, 3, 128, 128))
    f = UNET(1)
    y = f(x)
    print(x.shape)
    print(y.shape)

    end=time.time()
    
    print(f'spending time :  {end-start}')


