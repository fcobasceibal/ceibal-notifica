#!/usr/bin/python
# -*- coding: utf-8 -*-
# 2015-03 - Plan CEIBAL Uruguay
# Autor: Francisco Cobas - fcobas@plan.ceibal.edu.uy
#
# Descarga las notificaciones encontradas
# Ultima modificacion: 2015-03

import commands
import os
import sys
import time
import random
import logging
import logging.handlers
import json

from ceibal.notifier import env as notif_env
from ceibal import env
from ceibal import util


#from ceibalmipc.laptops.laptopFactory import LaptopFactory


WORK_DIR = notif_env.get_work_dir()
DIR_SEGURIDAD = env.get_security_root()
NOTIHOY = os.path.join(WORK_DIR, "notihoy")


def already_running():
    command = 'ps -ef | grep notificador-crear.py | grep -v grep | wc -l'
    status, output = commands.getstatusoutput(command)
    if not status:
        if int(output) <= 2:
            return False
        else:
            return True
    return False

class NotificadorObtener:

    def __init__(self, onDemand=False):
        self.__set_logger()

        # Realiza el chequeo de los directorios necesarios para la ejecucion
        self.chk_env()

        self._logger.debug("Inicio proceso de obtencion de notificaciones ...")

        self._updated_today = os.path.join(WORK_DIR, "notihoy")

        if self.already_checked_for_noti(onDemand):
            self._logger.info(time.ctime() + ' -AVISO: Ya se chequearon las notificaciones en este periodo. Volvera a chequear cuando comience el siguiente periodo. Saliendo...')
            exit()

        time_wait = 60
        espera = random.randint(0, time_wait)
        self._logger.info('Esperando %i segundos...' %espera)
        time.sleep(espera)

        # Importamos la clase W_S_Conexion para conectarons al Web Service.
        from ceibal.notifier.web_service_conexion import W_S_Conexion

        # Importamos las Constantes.
        from ceibal.notifier.constantes import WEB_SERVICE_URL

        # Realizamos la coneccion con el Web Service.
        web = W_S_Conexion(WEB_SERVICE_URL)

        # Obtenemos las notificaciones
        json_response = web.Obtener_notificaciones(False)

        if json_response is not None:
            contenido = json.loads(json_response)
            frecuencia_obtener = contenido['frecuencia_muestro']
            # Seteamos la hora en el notihoy
            self.__set_update_today(frecuencia_obtener)

        self._logger.info(time.ctime() + '- Se termino el proceso de obtener notificaciones. Saliendo...')



    def __set_update_today(self, frecuencia_obtener):
        '''
        Marca cuando se llamo al WebService
        '''
        try:
            # el parametro viene en horas, y necesito tener los segundos.
            tiempo = int(frecuencia_obtener) * 60 * 60
        except Exception as e:
            print (e)

        data = str(time.time()).split('.')[0] + ';'
        data += str(tiempo) + ';'

        util.data_2_file(data, self._updated_today)

    def already_checked_for_noti(self, onDemand):
        '''
        Retorna True si ya se actualizo hoy
        '''
        retorno = False

        try:
            f = open(self._updated_today, 'r')
        except:
            return False

        data = f.read()

        horaActualizado = int(data.split(';')[0])
        tiempoActualizacion = int(data.split(';')[1])
        f.close()

        if onDemand is False:
            horaActual = int(str(time.time()).split('.')[0])
            diffHoras = horaActual - horaActualizado
            if diffHoras < tiempoActualizacion:
                retorno = True
        
        return retorno


    def __set_logger(self):
        FILE_LOG = os.path.join(WORK_DIR, 'notificador.log')

        # create a file handler
        handler = logging.FileHandler(FILE_LOG)
        handler.setLevel(logging.DEBUG)

        # create a logging format
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.INFO)
        self._logger.addHandler(handler)

    def chk_env(self):
        '''
        Realiza el chequeo de los directorios y archivos necesarios para que
        funcione el programa.
        De no existir algun directorio necesario lo crea y le da permisos.
        '''
        if WORK_DIR is None:
            self._logger.error(time.ctime() + '- No se encontro el directorio: ' + WORK_DIR + ' - saliendo...')
            exit()

        if not os.path.isdir(WORK_DIR):
            os.makedirs(WORK_DIR, 0744)

        if not os.path.exists(NOTIHOY):
            f=open(NOTIHOY, 'w')
            f.write('00000000;100;')
            f.close()

        os.chmod(NOTIHOY, 0666)



#############################################################
# main
#############################################################

if __name__ == "__main__":

    if already_running():
        exit()

    # Hace el proceso de 
    notificacionesObtener = NotificadorObtener()