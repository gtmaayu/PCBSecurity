/*******************************************************************************
  CLOCK PLIB

  Company:
    Microchip Technology Inc.

  File Name:
    plib_clock.c

  Summary:
    CLOCK PLIB Implementation File.

  Description:
    None

*******************************************************************************/

// DOM-IGNORE-BEGIN
/*******************************************************************************
* Copyright (C) 2019 Microchip Technology Inc. and its subsidiaries.
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

#include "plib_clock.h"
//#include "device.h"
//#include "interrupts.h"
#include <Arduino.h>
#include "gclk.h"
#include "sysctrl.h"
// *****************************************************************************
// *****************************************************************************
// Section: CLOCK Interface Routines
// *****************************************************************************
// *****************************************************************************

void SYSCTRL_Initialize( void )
{
    SYSCTRL->OSC32K.reg = 0x0U;
}


void DFLL_Initialize( void )
{
    /****************** DFLL Initialization  *********************************/

    SYSCTRL->DFLLCTRL.reg &= (uint16_t)(~SYSCTRL_DFLLCTRL_ONDEMAND_Msk);

    while((SYSCTRL->PCLKSR.reg & SYSCTRL_PCLKSR_DFLLRDY_Msk) != SYSCTRL_PCLKSR_DFLLRDY_Msk)
    {
        /* Waiting for the Ready state */
    }

    /* Load Calibration Value */
    uint8_t calibCoarse = (uint8_t)(((*((uint32_t*)0x00806020U + 1U)) >> 26U ) & 0x3fU);
    calibCoarse = (((calibCoarse) == 0x3FU) ? 0x1FU : (calibCoarse));

    SYSCTRL->DFLLVAL.reg = SYSCTRL_DFLLVAL_COARSE((uint32_t)calibCoarse) | SYSCTRL_DFLLVAL_FINE((uint32_t)512U);

    while((SYSCTRL->PCLKSR.reg & SYSCTRL_PCLKSR_DFLLRDY_Msk) != SYSCTRL_PCLKSR_DFLLRDY_Msk)
    {
        /* Waiting for the Ready state */
    }

    /* Configure DFLL */
    SYSCTRL->DFLLCTRL.reg = SYSCTRL_DFLLCTRL_ENABLE_Msk ;

    while((SYSCTRL->PCLKSR.reg & SYSCTRL_PCLKSR_DFLLRDY_Msk) != SYSCTRL_PCLKSR_DFLLRDY_Msk)
    {
        /* Waiting for DFLL to be ready */
    }
    
}



void GCLK1_Initialize( void )
{

    GCLK->GENCTRL.reg = GCLK_GENCTRL_SRC(6U) | GCLK_GENCTRL_GENEN_Msk | GCLK_GENCTRL_ID(1U);

    while((GCLK->STATUS.reg & GCLK_STATUS_SYNCBUSY_Msk) == GCLK_STATUS_SYNCBUSY_Msk)
    {
        /* wait for the Generator 0 synchronization */
    }
}

// void CLOCK_Initialize( void )
// {
//     // Function to Initialize the Oscillators 
//     SYSCTRL_Initialize();

//     DFLL_Initialize();
//     GCLK0_Initialize();


//     /* Selection of the Generator and write Lock for EIC */
//     GCLK_REGS->GCLK_CLKCTRL = GCLK_CLKCTRL_ID(5U) | GCLK_CLKCTRL_GEN(0x0U)  | GCLK_CLKCTRL_CLKEN_Msk;

//     /* Selection of the Generator and write Lock for SERCOM2_CORE */
//     GCLK_REGS->GCLK_CLKCTRL = GCLK_CLKCTRL_ID(16U) | GCLK_CLKCTRL_GEN(0x0U)  | GCLK_CLKCTRL_CLKEN_Msk;

//     /* Selection of the Generator and write Lock for ADC */
//     GCLK_REGS->GCLK_CLKCTRL = GCLK_CLKCTRL_ID(19U) | GCLK_CLKCTRL_GEN(0x0U)  | GCLK_CLKCTRL_CLKEN_Msk;

//     /* Selection of the Generator and write Lock for DAC */
//     GCLK_REGS->GCLK_CLKCTRL = GCLK_CLKCTRL_ID(22U) | GCLK_CLKCTRL_GEN(0x0U)  | GCLK_CLKCTRL_CLKEN_Msk;


//     /* Configure the APBC Bridge Clocks */
//     PM_REGS->PM_APBCMASK = 0x510U;


//     /* Disable RC oscillator */
//     SYSCTRL_REGS->SYSCTRL_OSC8M = 0x0U;
// }

