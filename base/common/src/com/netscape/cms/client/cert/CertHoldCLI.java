// --- BEGIN COPYRIGHT BLOCK ---
// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; version 2 of the License.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License along
// with this program; if not, write to the Free Software Foundation, Inc.,
// 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
//
// (C) 2012 Red Hat, Inc.
// All rights reserved.
// --- END COPYRIGHT BLOCK ---

package com.netscape.cms.client.cert;

import java.io.BufferedReader;
import java.io.InputStreamReader;

import netscape.security.x509.RevocationReason;

import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.Option;

import com.netscape.certsrv.dbs.certdb.CertId;
import com.netscape.certsrv.request.RequestStatus;
import com.netscape.cms.client.cli.CLI;
import com.netscape.cms.client.cli.MainCLI;
import com.netscape.cms.servlet.cert.model.CertRevokeRequest;
import com.netscape.cms.servlet.cert.model.CertData;
import com.netscape.cms.servlet.request.model.CertRequestInfo;

/**
 * @author Endi S. Dewata
 */
public class CertHoldCLI extends CLI {

    public CertCLI parent;

    public CertHoldCLI(CertCLI parent) {
        super("hold", "Place certificate on-hold");
        this.parent = parent;
    }

    public void printHelp() {
        formatter.printHelp(parent.name + "-" + name + " <Serial Number> [OPTIONS...]", options);
    }

    public void execute(String[] args) throws Exception {

        Option option = new Option(null, "comments", true, "Comments");
        option.setArgName("comments");
        options.addOption(option);

        options.addOption(null, "force", false, "Force");

        CommandLine cmd = null;

        try {
            cmd = parser.parse(options, args);

        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
            printHelp();
            System.exit(1);
        }

        String[] cmdArgs = cmd.getArgs();

        if (cmdArgs.length != 1) {
            printHelp();
            System.exit(1);
        }

        CertId certID = new CertId(cmdArgs[0]);

        if (!cmd.hasOption("force")) {

            CertData certData = parent.client.getCert(certID);

            System.out.println("Placing certificate on-hold:");

            CertCLI.printCertData(certData, false, false);

            System.out.print("Are you sure (Y/N)? ");
            System.out.flush();

            BufferedReader reader = new BufferedReader(new InputStreamReader(System.in));
            String line = reader.readLine();
            if (!line.equalsIgnoreCase("Y")) {
                System.exit(1);
            }
        }

        CertRevokeRequest request = new CertRevokeRequest();
        request.setReason(RevocationReason.CERTIFICATE_HOLD);
        request.setComments(cmd.getOptionValue("comments"));

        CertRequestInfo certRequestInfo = parent.client.revokeCert(certID, request);

        if (verbose) {
            CertCLI.printCertRequestInfo(certRequestInfo);
        }

        if (certRequestInfo.getRequestStatus() == RequestStatus.COMPLETE) {
            MainCLI.printMessage("Placed certificate \"" + certID.toHexString() + "\" on-hold");
            CertData certData = parent.client.getCert(certID);
            CertCLI.printCertData(certData, false, false);

        } else {
            MainCLI.printMessage("Request \"" + certRequestInfo.getRequestId() + "\": " + certRequestInfo.getRequestStatus());
        }
    }
}
