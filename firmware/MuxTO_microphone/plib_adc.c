/*******************************************************************************
  Analog-to-Digital Converter(ADC) PLIB

  Company
    Microchip Technology Inc.

  File Name
    plib_adc.c

  Summary
    ADC PLIB Implementation File.

  Description
    This file defines the interface to the ADC peripheral library. This
    library provides access to and control of the associated peripheral
    instance.

  Remarks:
    None.

*******************************************************************************/

// DOM-IGNORE-BEGIN
/*******************************************************************************
* Copyright (C) 2018 Microchip Technology Inc. and its subsidiaries.
*
* Subject to your compliance with these terms, you may use Microchip software
* and any derivatives exclusively with Microchip products. It is your
* responsibility to comply with third party license terms applicable to your
* use of third party software (including open source software) that may
* accompany Microchip software.
*
* THIS SOFTWARE IS SUPPLIED BY MICROCHIP "AS IS". NO WARRANTIES, WHETHER
* EXPRESS, IMPLIED OR STATUTORY, APPLY TO THIS SOFTWARE, INCLUDING ANY IMPLIED
* WARRANTIES OF NON-INFRINGEMENT, MERCHANTABILITY, AND FITNESS FOR A
* PARTICULAR PURPOSE.
*
* IN NO EVENT WILL MICROCHIP BE LIABLE FOR ANY INDIRECT, SPECIAL, PUNITIVE,
* INCIDENTAL OR CONSEQUENTIAL LOSS, DAMAGE, COST OR EXPENSE OF ANY KIND
* WHATSOEVER RELATED TO THE SOFTWARE, HOWEVER CAUSED, EVEN IF MICROCHIP HAS
* BEEN ADVISED OF THE POSSIBILITY OR THE DAMAGES ARE FORESEEABLE. TO THE
* FULLEST EXTENT ALLOWED BY LAW, MICROCHIP'S TOTAL LIABILITY ON ALL CLAIMS IN
* ANY WAY RELATED TO THIS SOFTWARE WILL NOT EXCEED THE AMOUNT OF FEES, IF ANY,
* THAT YOU HAVE PAID DIRECTLY TO MICROCHIP FOR THIS SOFTWARE.
*******************************************************************************/
// DOM-IGNORE-END

// *****************************************************************************
// *****************************************************************************
// Section: Included Files
// *****************************************************************************
// *****************************************************************************
/* This section lists the other files that are included in this file.
*/

#include "plib_adc.h"
// #include "interrupts.h"
#include <Arduino.h>
// #include "wiring_private.h"
#include "adc.h"

// *****************************************************************************
// *****************************************************************************
// Section: Global Data
// *****************************************************************************
// *****************************************************************************

#define ADC_LINEARITY0_POS  (27U)
#define ADC_LINEARITY0_Msk   ((0x1FUL << ADC_LINEARITY0_POS))

#define ADC_LINEARITY1_POS  (0U)
#define ADC_LINEARITY1_Msk   ((0x7U << ADC_LINEARITY1_POS))

#define ADC_BIASCAL_POS  (3U)
#define ADC_BIASCAL_Msk   ((0x7U << ADC_BIASCAL_POS))

#define ADC_SELECTED_GAIN ADC_INPUTCTRL_GAIN_1X

#define OTP4_ADDR                      _UINT32_(0x00806020)    /* OTP4 base address (type: fuses)*/

#define GCLK_CLKCTRL_CLKEN_Pos                _UINT16_(14)                                         /* (GCLK_CLKCTRL) Clock Enable Position */
#define GCLK_CLKCTRL_CLKEN_Msk                (_UINT16_(0x1) << GCLK_CLKCTRL_CLKEN_Pos)            /* (GCLK_CLKCTRL) Clock Enable Mask */

// *****************************************************************************
// *****************************************************************************
// Section: ADC Implementation
// *****************************************************************************
// *****************************************************************************

// *****************************************************************************
/* Initialize ADC module */

void CLOCK_Initialize( void )
{
    /* Function to Initialize the Oscillators */
    //SYSCTRL_Initialize();

   // DFLL_Initialize();
   GCLK1_Initialize();


    // /* Selection of the Generator and write Lock for EIC */
    // GCLK_REGS->GCLK_CLKCTRL = GCLK_CLKCTRL_ID(5U) | GCLK_CLKCTRL_GEN(0x0U)  | GCLK_CLKCTRL_CLKEN_Msk;

    // /* Selection of the Generator and write Lock for SERCOM2_CORE */
    // GCLK_REGS->GCLK_CLKCTRL = GCLK_CLKCTRL_ID(16U) | GCLK_CLKCTRL_GEN(0x0U)  | GCLK_CLKCTRL_CLKEN_Msk;

    /* Selection of the Generator and write Lock for ADC */
    GCLK->CLKCTRL.reg = GCLK_CLKCTRL_ID(19U) | GCLK_CLKCTRL_GEN(0x1U)  | GCLK_CLKCTRL_CLKEN_Msk;

    // /* Selection of the Generator and write Lock for DAC */
    // GCLK_REGS->GCLK_CLKCTRL = GCLK_CLKCTRL_ID(22U) | GCLK_CLKCTRL_GEN(0x0U)  | GCLK_CLKCTRL_CLKEN_Msk;


    // /* Configure the APBC Bridge Clocks */
    //PM->APBCMASK.reg = 0x510U;
    PM->APBCMASK.reg |= PM_APBCMASK_ADC;

   
   // PM->APBCMASK.bit.ADC_ = 0x1u;
    //PM->APBCMASK.bit.AC_ = 0x1u;
    //PM->APBCMASK.bit.TCC0_ = 0x1u;



    // /* Disable RC oscillator */
    //SYSCTRL->OSC8M.reg = 0x0U;
}

void ADC_Initialize( void )
{
    /* Reset ADC */
    ADC->CTRLA.reg = ADC_CTRLA_SWRST_Msk;

    while((ADC->STATUS.reg & ADC_STATUS_SYNCBUSY_Msk)!= 0U)
    {
        /* Wait for Synchronization */
    }

    uint32_t adc_linearity0 = (((*(uint32_t*)OTP4_ADDR) & ADC_LINEARITY0_Msk) >> ADC_LINEARITY0_POS);
    uint32_t adc_linearity1 = (((*(uint32_t*)(OTP4_ADDR + 4U)) & ADC_LINEARITY1_Msk) >> ADC_LINEARITY1_POS);

    /* Write linearity calibration and bias calibration */
    ADC->CALIB.reg = (uint16_t)((ADC_CALIB_LINEARITY_CAL(adc_linearity0 | (adc_linearity1 << 5U))) \
        | ADC_CALIB_BIAS_CAL((((*(uint32_t*)(OTP4_ADDR + 4U)) & ADC_BIASCAL_Msk) >> ADC_BIASCAL_POS)));

    /* Sampling length */
    ADC->SAMPCTRL.reg = ADC_SAMPCTRL_SAMPLEN(1U);

    /* reference */
    ADC->REFCTRL.reg = ADC_REFCTRL_REFSEL_INTVCC0;

    /* positive and negative input pins */
    ADC->INPUTCTRL.reg = (uint32_t) ADC_POSINPUT_PIN0 | (uint32_t) ADC_NEGINPUT_GND \
        | ADC_INPUTCTRL_INPUTSCAN(0U) | ADC_INPUTCTRL_INPUTOFFSET(0U) | ADC_SELECTED_GAIN;
    while((ADC->STATUS.reg & ADC_STATUS_SYNCBUSY_Msk)!= 0U)
    {
        /* Wait for Synchronization */
    }

    /* Prescaler, Resolution & Operation Mode */
    ADC->CTRLB.reg = ADC_CTRLB_PRESCALER_DIV4 | ADC_CTRLB_RESSEL_12BIT ;
    while((ADC->STATUS.reg & ADC_STATUS_SYNCBUSY_Msk)!= 0U)
    {
        /* Wait for Synchronization */
    }

    /* Clear all interrupt flags */
    ADC->INTFLAG.reg = ADC_INTFLAG_Msk;

    while((ADC->STATUS.reg & ADC_STATUS_SYNCBUSY_Msk) != 0U)
    {
        /* Wait for Synchronization */
    }
}

/* Enable ADC module */
void ADC_Enable( void )
{
    ADC->CTRLA.reg |= ADC_CTRLA_ENABLE_Msk;
    while((ADC->STATUS.reg & ADC_STATUS_SYNCBUSY_Msk) != 0U)
    {
        /* Wait for Synchronization */
    }
}

void PORT_Initialize(void)
{
   /************************** GROUP 0 Initialization *************************/
   PORT->Group[0].DIRCLR.reg = 0x4U; // Configure as input
   PORT->Group[0].PMUX[1].reg &= 0xF0U;
   PORT->Group[0].PMUX[1].reg |= 0x1U;  // Select mode B

   PORT->Group[0].PINCFG[2].bit.PMUXEN = 0x1U;

}

/* Disable ADC module */
void ADC_Disable( void )
{
    ADC->CTRLA.reg = ((ADC->CTRLA.reg) & (uint8_t)(~ADC_CTRLA_ENABLE_Msk));
    while((ADC->STATUS.reg & ADC_STATUS_SYNCBUSY_Msk) != 0U)
    {
        /* Wait for Synchronization */
    }
}

/* Configure channel input */
void ADC_ChannelSelect( ADC_POSINPUT positiveInput, ADC_NEGINPUT negativeInput )
{
    /* Configure positive and negative input pins */
    uint32_t channel;
    channel = ADC->INPUTCTRL.reg;
    channel &= ~(ADC_INPUTCTRL_MUXPOS_Msk | ADC_INPUTCTRL_MUXNEG_Msk);
    channel |= (uint32_t) positiveInput | (uint32_t) negativeInput;
    ADC->INPUTCTRL.reg = channel;

    while((ADC->STATUS.reg & ADC_STATUS_SYNCBUSY_Msk) != 0U)
    {
        /* Wait for Synchronization */
    }
}

/* Start the ADC conversion by SW */
void ADC_ConversionStart( void )
{
    /* Start conversion */
    ADC->SWTRIG.reg |= ADC_SWTRIG_START_Msk;

    while((ADC->STATUS.reg & ADC_STATUS_SYNCBUSY_Msk) != 0U)
    {
        /* Wait for Synchronization */
    }
}

/* Configure window comparison threshold values */
void ADC_ComparisonWindowSet(uint16_t low_threshold, uint16_t high_threshold)
{
    ADC->WINLT.reg = low_threshold;
    while((ADC->STATUS.reg & ADC_STATUS_SYNCBUSY_Msk) != 0U)
    {
        /* Wait for Synchronization */
    }
    ADC->WINUT.reg = high_threshold;
    while((ADC->STATUS.reg & ADC_STATUS_SYNCBUSY_Msk) != 0U)
    {
        /* Wait for Synchronization */
    }
}

void ADC_WindowModeSet(ADC_WINMODE mode)
{
    ADC->WINCTRL.reg = (uint8_t)mode << ADC_WINCTRL_WINMODE_Pos;
    while((ADC->STATUS.reg & ADC_STATUS_SYNCBUSY_Msk) != 0U)
    {
        /* Wait for Synchronization */
    }
}


/* Read the conversion result */
uint16_t ADC_ConversionResultGet( void )
{
    while((ADC->STATUS.reg & ADC_STATUS_SYNCBUSY_Msk)!= 0U)
    {
        /* Wait for Synchronization */
    }
    return (uint16_t)ADC->RESULT.reg;
}

void ADC_InterruptsClear(ADC_STATUS interruptMask)
{
    ADC->INTFLAG.reg = interruptMask;
}

void ADC_InterruptsEnable(ADC_STATUS interruptMask)
{
    ADC->INTENSET.reg = interruptMask;
}

void ADC_InterruptsDisable(ADC_STATUS interruptMask)
{
    ADC->INTENCLR.reg = interruptMask;
}


/* Check whether result is ready */
bool ADC_ConversionStatusGet( void )
{
    bool status;
    status =  (((ADC->INTFLAG.reg & ADC_INTFLAG_RESRDY_Msk) >> ADC_INTFLAG_RESRDY_Pos)!= 0U);
    if (status == true)
    {
        ADC->INTFLAG.reg = ADC_INTFLAG_RESRDY_Msk;
    }
    return status;
}
